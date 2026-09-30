"""
Sentinel Agent — fuses weather + trends + IDSP + stock into a district risk score.
Uses Gemini when configured. Mock fallback is always labelled `ai_source=mock`.
"""

from __future__ import annotations

import json

from agents.gemini_client import GeminiUnavailable, friendly_error, generate_json, mocks_allowed
from data.mock_phcs import DISTRICTS, STATE_META, state_for_district
from signals.weather import get_weather_signal
from signals.trends import get_trends_signal, get_simulated_outbreak_trends
from signals.idsp import get_idsp_signal


def _days_of_supply(phc: dict, medicine: str) -> int:
    stock = phc["stock"].get(medicine, 0)
    daily_consumption = max(1, phc["avg_daily_footfall"] * 0.15)
    return int(stock / daily_consumption)


def _district_stock_summary(district_name: str, phcs: list[dict]) -> dict:
    district_phcs = [p for p in phcs if p["district"] == district_name]
    if not district_phcs:
        return {}

    summary = {}
    for medicine in ["ORS", "Paracetamol", "IronTablets", "IVFluids"]:
        days_list = [_days_of_supply(p, medicine) for p in district_phcs]
        summary[medicine] = {
            "avg_days_supply": round(sum(days_list) / len(days_list), 1),
            "critical_phcs": sum(1 for d in days_list if d < 7),
            "total_phcs": len(days_list),
        }
    return summary


async def run_sentinel(
    district: str,
    simulated: bool = False,
    outbreak_kind: str = "dengue",
    phcs: list[dict] | None = None,
) -> dict:
    from data.mock_phcs import MOCK_PHCS

    district_info = DISTRICTS.get(district, {})
    lat = district_info.get("lat", 18.5)
    lng = district_info.get("lng", 73.8)
    state = state_for_district(district)
    geo = STATE_META.get(state, {}).get("geo_code", "IN-MH")

    import asyncio

    weather, trends = await asyncio.gather(
        get_weather_signal(lat, lng),
        get_simulated_outbreak_trends(outbreak_kind) if simulated else get_trends_signal(geo),
    )
    idsp = get_idsp_signal(district, simulated=simulated)
    stock = _district_stock_summary(district, phcs or MOCK_PHCS)

    signals = {
        "district": district,
        "state": state,
        "weather": weather,
        "google_trends": trends,
        "idsp": idsp,
        "stock_summary": stock,
    }

    prompt = f"""You are an epidemiologist AI monitoring India's Primary Health Centre network.

Analyse these signals for {district} district, {state}:

WEATHER: {json.dumps(weather)}
GOOGLE TRENDS (symptom searches): {json.dumps(trends)}
IDSP-STYLE CASE COUNTS (demo baseline, not a live MoHFW feed): {json.dumps(idsp)}
MEDICINE STOCK (avg days of supply): {json.dumps(stock)}

Return ONLY valid JSON:
{{
  "risk_score": <integer 0-100>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "primary_driver": "<single most important risk factor>",
  "days_to_surge": <integer>,
  "key_medicines_at_risk": ["<medicine>", "..."],
  "reasoning": "<2-3 sentences a district CMO would understand>",
  "recommended_action": "<specific actionable recommendation>"
}}"""

    try:
        result = generate_json(prompt)
        result["signals"] = signals
        result["district"] = district
        result["state"] = state
        return result
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        mock = _mock_sentinel_response(district, signals, simulated, outbreak_kind)
        mock["ai_error"] = friendly_error(exc)
        return mock


async def run_sentinel_many(
    districts: list[str],
    *,
    simulated_for: set[str] | None = None,
    outbreak_kind: str = "dengue",
    phcs: list[dict] | None = None,
) -> list[dict]:
    """Score many districts in one Gemini call so a demo does not burn the free-tier quota."""
    from data.mock_phcs import MOCK_PHCS
    import asyncio

    simulated_for = simulated_for or set()
    stock_phcs = phcs or MOCK_PHCS
    packed = []
    for district in districts:
        district_info = DISTRICTS.get(district, {})
        lat = district_info.get("lat", 18.5)
        lng = district_info.get("lng", 73.8)
        state = state_for_district(district)
        geo = STATE_META.get(state, {}).get("geo_code", "IN-MH")
        simulated = district in simulated_for
        weather, trends = await asyncio.gather(
            get_weather_signal(lat, lng),
            get_simulated_outbreak_trends(outbreak_kind) if simulated else get_trends_signal(geo),
        )
        idsp = get_idsp_signal(district, simulated=simulated)
        stock = _district_stock_summary(district, stock_phcs)
        signals = {
            "district": district,
            "state": state,
            "weather": weather,
            "google_trends": trends,
            "idsp": idsp,
            "stock_summary": stock,
            "simulated_outbreak": simulated,
        }
        packed.append({"district": district, "state": state, "simulated": simulated, "signals": signals})

    prompt = f"""You are an epidemiologist AI monitoring India's Primary Health Centre network.

Score EVERY district below. Outbreak-injected districts are flagged simulated_outbreak=true.

SIGNALS: {json.dumps([p["signals"] for p in packed], default=str)}

Return ONLY valid JSON:
{{
  "assessments": [
    {{
      "district": "<name>",
      "risk_score": <integer 0-100>,
      "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
      "primary_driver": "<single most important risk factor>",
      "days_to_surge": <integer>,
      "key_medicines_at_risk": ["<medicine>"],
      "reasoning": "<2-3 sentences a district CMO would understand>",
      "recommended_action": "<specific actionable recommendation>"
    }}
  ]
}}"""

    try:
        data = generate_json(prompt)
        by_name = {}
        for row in data.get("assessments") or []:
            if isinstance(row, dict) and row.get("district"):
                by_name[str(row["district"]).strip().lower()] = row
        results = []
        for item in packed:
            row = by_name.get(item["district"].lower())
            if not row:
                mock = _mock_sentinel_response(item["district"], item["signals"], item["simulated"], outbreak_kind)
                mock["ai_error"] = "Gemini omitted this district; using labelled mock."
                results.append(mock)
                continue
            row["signals"] = item["signals"]
            row["district"] = item["district"]
            row["state"] = item["state"]
            row["ai_source"] = data.get("ai_source", "gemini")
            row["ai_model"] = data.get("ai_model")
            results.append(row)
        return results
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        note = friendly_error(exc)
        results = []
        for item in packed:
            mock = _mock_sentinel_response(item["district"], item["signals"], item["simulated"], outbreak_kind)
            mock["ai_error"] = note
            results.append(mock)
        return results


def _mock_sentinel_response(district: str, signals: dict, simulated: bool, outbreak_kind: str) -> dict:
    mock_data = {
        "Raigad": {
            "risk_score": 87 if simulated else 62,
            "risk_level": "CRITICAL" if simulated else "HIGH",
            "primary_driver": "Dengue search trends +360% above baseline combined with early monsoon onset",
            "days_to_surge": 8 if simulated else 14,
            "key_medicines_at_risk": ["ORS", "IronTablets", "IVFluids"],
            "reasoning": "Google Trends shows dengue symptom searches 3.6x above baseline in Marathi. Early monsoon by 9 days extends vector season. ORS stock critically low at PHC Mahad (3-day supply).",
            "recommended_action": "Emergency pre-positioning of 2,400 ORS units and 800 IV fluid bags from Nashik surplus. Execute within 48 hours.",
        },
        "Pune": {
            "risk_score": 45 if simulated else 38,
            "risk_level": "MEDIUM",
            "primary_driver": "Moderate dengue trend increase, stock levels adequate",
            "days_to_surge": 21,
            "key_medicines_at_risk": ["IronTablets"],
            "reasoning": "Dengue searches up 48% but from a low baseline. Stock levels healthy across most medicines. Iron tablets running low in 2 PHCs.",
            "recommended_action": "Monitor dengue trends for next 7 days. Replenish iron tablets at PHC Hadapsar and PHC Khed.",
        },
        "Nashik": {
            "risk_score": 18,
            "risk_level": "LOW",
            "primary_driver": "Stock surplus, low disease surveillance signals",
            "days_to_surge": 45,
            "key_medicines_at_risk": [],
            "reasoning": "All medicine stocks above 30-day supply. Disease surveillance normal. Weather signals below threshold.",
            "recommended_action": "Available for cross-district redistribution. 3,200 ORS units and 1,400 IV fluids available for transfer.",
        },
        "Thane": {
            "risk_score": 55 if simulated else 42,
            "risk_level": "HIGH" if simulated else "MEDIUM",
            "primary_driver": "Rising fever and diarrhea trends, monsoon corridor",
            "days_to_surge": 14 if simulated else 22,
            "key_medicines_at_risk": ["ORS", "Artemisinin"],
            "reasoning": "Fever searches in Thane up 43%. PHC Murbad showing low ORS and IV fluid stocks. Monsoon corridor from Mumbai increases transmission risk.",
            "recommended_action": "Pre-position 800 ORS units in Murbad block. Monitor Artemisinin stock.",
        },
        "Puri": {
            "risk_score": 91 if simulated else 70,
            "risk_level": "CRITICAL" if simulated else "HIGH",
            "primary_driver": "Post-flood diarrheal surge with ORS stock-out risk on the Puri coast",
            "days_to_surge": 5 if simulated else 11,
            "key_medicines_at_risk": ["ORS", "IVFluids"],
            "reasoning": "Diarrhea searches in Odisha +243% vs baseline after coastal flooding. PHC Konark has a 2-day ORS supply. IDSP-style counts show diarrhea 5x weekly baseline in Puri.",
            "recommended_action": "Move 2,000 ORS units and 600 IV fluid bags from Cuttack surplus within 36 hours.",
        },
        "Cuttack": {
            "risk_score": 16,
            "risk_level": "LOW",
            "primary_driver": "Inland surplus district, surveillance within range",
            "days_to_surge": 40,
            "key_medicines_at_risk": [],
            "reasoning": "ORS and IV fluid stocks above 30-day supply. Flood impact is coastal; Cuttack can donate to Puri and Balasore.",
            "recommended_action": "Hold 2,500 ORS units ready for intra-state redistribution.",
        },
        "Khordha": {
            "risk_score": 44 if simulated else 36,
            "risk_level": "MEDIUM",
            "primary_driver": "Moderate flood spillover, stocks adequate",
            "days_to_surge": 18,
            "key_medicines_at_risk": ["ORS"],
            "reasoning": "Diarrhea signals elevated but stocks at Jatni remain above 14-day supply. Monitor overnight camps.",
            "recommended_action": "Keep a 400-unit ORS buffer at Jatni. No transfer required yet.",
        },
        "Balasore": {
            "risk_score": 68 if simulated else 48,
            "risk_level": "HIGH" if simulated else "MEDIUM",
            "primary_driver": "Flood corridor with rising diarrhea and strained staffing",
            "days_to_surge": 9 if simulated else 16,
            "key_medicines_at_risk": ["ORS", "IVFluids"],
            "reasoning": "Balasore Sadar occupancy is high and ORS days-of-supply is tight. Flood water has not receded in Remuna block.",
            "recommended_action": "Pre-position 700 ORS units from Cuttack. Review Monday staff absences.",
        },
        "Barmer": {
            "risk_score": 88 if simulated else 58,
            "risk_level": "CRITICAL" if simulated else "HIGH",
            "primary_driver": "Desert malaria surge with critically low Artemisinin and ORS",
            "days_to_surge": 6 if simulated else 12,
            "key_medicines_at_risk": ["Artemisinin", "ORS", "IVFluids"],
            "reasoning": "Malaria searches in Rajasthan +280% vs baseline. PHC Siwana has a 2-day Artemisinin supply. Heat is driving ORS use alongside vector cases in Barmer block.",
            "recommended_action": "Move 900 Artemisinin courses and 1,600 ORS units from Jodhpur surplus within 48 hours.",
        },
        "Jodhpur": {
            "risk_score": 17,
            "risk_level": "LOW",
            "primary_driver": "Stock surplus, malaria signals within range",
            "days_to_surge": 40,
            "key_medicines_at_risk": [],
            "reasoning": "ORS and Artemisinin stocks above 30-day supply at Jodhpur Rural and Osian. Available as the Rajasthan donor district.",
            "recommended_action": "Hold Artemisinin and ORS ready for Barmer and Udaipur if scores rise.",
        },
        "Jaipur": {
            "risk_score": 42 if simulated else 34,
            "risk_level": "MEDIUM",
            "primary_driver": "Urban dengue watch, stocks adequate",
            "days_to_surge": 20,
            "key_medicines_at_risk": ["Paracetamol"],
            "reasoning": "Fever searches up modestly in Jaipur. Amber and Chomu PHCs have comfortable ORS days-of-supply.",
            "recommended_action": "Monitor dengue for 7 days. No intra-state transfer required yet.",
        },
        "Udaipur": {
            "risk_score": 61 if simulated else 44,
            "risk_level": "HIGH" if simulated else "MEDIUM",
            "primary_driver": "Southern malaria belt with tightening Artemisinin",
            "days_to_surge": 11 if simulated else 18,
            "key_medicines_at_risk": ["Artemisinin", "ORS"],
            "reasoning": "Udaipur Girwa malaria counts are elevated versus baseline. Salumber stock is tighter than Jodhpur but not yet critical.",
            "recommended_action": "Pre-position 400 Artemisinin courses from Jodhpur if Barmer transfer leaves surplus.",
        },
    }
    result = mock_data.get(district, {
        "risk_score": 30, "risk_level": "LOW",
        "primary_driver": "No significant signals detected",
        "days_to_surge": 30, "key_medicines_at_risk": [],
        "reasoning": "All signals within normal range.",
        "recommended_action": "Continue routine monitoring.",
    })
    result = dict(result)
    result["signals"] = signals
    result["district"] = district
    result["state"] = state_for_district(district)
    result["ai_source"] = "mock"
    result["ai_model"] = None
    return result
