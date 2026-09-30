"""
Coordinator Agent — surplus vs deficit districts → redistribution plan.
Prefers intra-state transfers so Maharashtra and Odisha share one model, not one warehouse.
"""

from __future__ import annotations

import json

from agents.gemini_client import GeminiUnavailable, friendly_error, generate_json, mocks_allowed
from data.mock_phcs import state_for_district


def _get_surplus_districts(all_risk: list[dict]) -> list[dict]:
    return [r for r in all_risk if r.get("risk_score", 100) < 25]


def _get_deficit_districts(all_risk: list[dict]) -> list[dict]:
    return [r for r in all_risk if r.get("risk_score", 0) > 60]


async def run_coordinator(all_risk_assessments: list[dict]) -> dict:
    surplus = _get_surplus_districts(all_risk_assessments)
    deficit = _get_deficit_districts(all_risk_assessments)

    if not deficit:
        return {
            "transfers": [],
            "summary": "No redistribution needed. All districts within safe thresholds.",
            "ai_source": "rule",
            "ai_model": None,
            "total_cost_inr": 0,
            "lives_protected_estimate": 0,
        }

    prompt = f"""You are a health supply chain coordinator for India's PHC network.

DISTRICTS NEEDING SUPPLIES (HIGH RISK):
{json.dumps(deficit, default=str)}

DISTRICTS WITH SURPLUS (LOW RISK):
{json.dumps(surplus, default=str)}

Rules:
- Prefer intra-state transfers (Maharashtra to Maharashtra, Odisha to Odisha).
- Only propose inter-state moves if the destination state has no surplus district.
- Transfer quantity based on days_to_surge and key_medicines_at_risk.
- Autonomy: quantity < 100 AUTO; 100-1000 APPROVE_REQUIRED; > 1000 ESCALATE.

Return ONLY valid JSON:
{{
  "transfers": [
    {{
      "id": "<unique_id>",
      "from_district": "<district>",
      "to_district": "<district>",
      "from_state": "<state>",
      "to_state": "<state>",
      "medicine": "<medicine_name>",
      "quantity": <integer>,
      "urgency": "<CRITICAL|HIGH|MEDIUM>",
      "deadline_days": <integer>,
      "estimated_cost_inr": <integer>,
      "justification": "<one sentence>",
      "autonomy_level": "<AUTO|APPROVE_REQUIRED|ESCALATE>"
    }}
  ],
  "total_cost_inr": <integer>,
  "lives_protected_estimate": <integer>,
  "summary": "<2 sentence overview>"
}}"""

    try:
        plan = generate_json(prompt)
        for t in plan.get("transfers", []):
            t.setdefault("status", "pending")
            t.setdefault("from_state", state_for_district(t.get("from_district", "")))
            t.setdefault("to_state", state_for_district(t.get("to_district", "")))
        return plan
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        mock = _mock_coordinator_response(surplus, deficit)
        mock["ai_error"] = friendly_error(exc)
        return mock


def _mock_coordinator_response(surplus: list, deficit: list) -> dict:
    transfers = []
    n = 1
    for dest in deficit:
        dest_name = dest.get("district")
        dest_state = dest.get("state") or state_for_district(dest_name)
        same = [s for s in surplus if (s.get("state") or state_for_district(s.get("district"))) == dest_state]
        pool = same or surplus
        if not pool:
            continue
        src = pool[0]
        src_name = src.get("district")
        src_state = src.get("state") or state_for_district(src_name)
        medicines = dest.get("key_medicines_at_risk") or ["ORS"]
        for i, med in enumerate(medicines[:2]):
            qty = 2400 if dest.get("risk_level") == "CRITICAL" and i == 0 else 700 if i == 0 else 500
            urgency = dest.get("risk_level") if dest.get("risk_level") in ("CRITICAL", "HIGH", "MEDIUM") else "HIGH"
            if urgency == "LOW":
                urgency = "MEDIUM"
            autonomy = "ESCALATE" if qty > 1000 else "APPROVE_REQUIRED"
            transfers.append({
                "id": f"TXF_{n:03d}",
                "from_district": src_name,
                "to_district": dest_name,
                "from_state": src_state,
                "to_state": dest_state,
                "medicine": med,
                "quantity": qty,
                "urgency": "CRITICAL" if dest.get("risk_score", 0) >= 85 else urgency,
                "deadline_days": 3 if dest.get("risk_score", 0) >= 85 else 6,
                "estimated_cost_inr": int(qty * 8),
                "justification": (
                    f"{dest_name} faces {med} stock-out in {dest.get('days_to_surge', 8)} days; "
                    f"{src_name} has surplus in {src_state}."
                ),
                "autonomy_level": autonomy,
                "status": "pending",
            })
            n += 1

    if not transfers:
        transfers = [
            {
                "id": "TXF_001",
                "from_district": "Nashik",
                "to_district": "Raigad",
                "from_state": "Maharashtra",
                "to_state": "Maharashtra",
                "medicine": "ORS",
                "quantity": 2400,
                "urgency": "CRITICAL",
                "deadline_days": 3,
                "estimated_cost_inr": 18400,
                "justification": "Raigad faces ORS stock-out with dengue surge predicted; Nashik has surplus.",
                "autonomy_level": "ESCALATE",
                "status": "pending",
            }
        ]

    total = sum(t["estimated_cost_inr"] for t in transfers)
    return {
        "transfers": transfers,
        "total_cost_inr": total,
        "lives_protected_estimate": 4200,
        "summary": "Intra-state redistribution generated from surplus districts. Acting now prevents estimated stock-outs at deficit PHCs.",
        "ai_source": "mock",
        "ai_model": None,
    }
