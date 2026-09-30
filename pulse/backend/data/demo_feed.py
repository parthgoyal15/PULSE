"""Seed transfers and alerts so Odisha and Rajasthan are never an empty demo."""

from __future__ import annotations

import datetime


def _ts(minutes_ago: int) -> str:
    return (datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_ago)).isoformat() + "Z"


def _wa(dest: str, src: str, med: str, qty: int, cost: int, days: int, urgency: str, lang: str) -> str:
    if lang == "or":
        local = (
            f"PULSE ସତର୍କତା — {dest} ଜିଲ୍ଲା\n"
            f"ବିପଦ: {urgency} | {days} ଦିନ ମଧ୍ୟରେ ଚାହିଦା ବୃଦ୍ଧି\n"
            f"ପ୍ରସ୍ତାବିତ ସ୍ଥାନାନ୍ତର: {qty} ୟୁନିଟ {med}\n"
            f"{src} → {dest} | ଆନୁମାନିକ ଖର୍ଚ୍ଚ ₹{cost:,}\n"
            f"ଉତ୍ତର ଦିଅନ୍ତୁ: Approve / Modify / Escalate"
        )
    elif lang == "hi":
        local = (
            f"PULSE चेतावनी — {dest}\n"
            f"जोखिम: {urgency} | {days} दिनों में मांग बढ़ सकती है\n"
            f"{qty} यूनिट {med} · {src} → {dest} | ₹{cost:,}\n"
            f"उत्तर दें: Approve / Modify / Escalate"
        )
    else:
        local = (
            f"PULSE इशारा — {dest} जिल्हा\n"
            f"धोका: {urgency} | {days} दिवसांत मागणी वाढण्याची शक्यता\n"
            f"प्रस्तावित हस्तांतरण: {qty} युनिट {med}\n"
            f"{src} → {dest} | अंदाजे खर्च ₹{cost:,}\n"
            f"उत्तर द्या: Approve / Modify / Escalate"
        )
    return (
        f"{local}\n\nEN: {urgency} — move {qty} {med} from {src} to {dest} "
        f"in {days} days (₹{cost:,}). Reply Approve, Modify, or Escalate."
    )


def demo_transfers() -> list[dict]:
    return [
        {
            "id": "TXF_MH_001",
            "from_district": "Nashik", "to_district": "Raigad",
            "from_state": "Maharashtra", "to_state": "Maharashtra",
            "medicine": "ORS", "quantity": 2400,
            "urgency": "CRITICAL", "deadline_days": 3, "estimated_cost_inr": 18400,
            "justification": "Raigad dengue + diarrhea surge; Nashik PHCs hold surplus ORS above 14-day cover.",
            "autonomy_level": "ESCALATE", "status": "pending",
            "whatsapp_language": "mr",
            "whatsapp_text": _wa("Raigad", "Nashik", "ORS", 2400, 18400, 3, "CRITICAL", "mr"),
        },
        {
            "id": "TXF_MH_002",
            "from_district": "Nashik", "to_district": "Raigad",
            "from_state": "Maharashtra", "to_state": "Maharashtra",
            "medicine": "IronTablets", "quantity": 500,
            "urgency": "CRITICAL", "deadline_days": 3, "estimated_cost_inr": 4000,
            "justification": "Multiple Raigad PHCs are below 5-day Iron tablet supply under outbreak load.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "mr",
            "whatsapp_text": _wa("Raigad", "Nashik", "IronTablets", 500, 4000, 3, "CRITICAL", "mr"),
        },
        {
            "id": "TXF_OD_001",
            "from_district": "Cuttack", "to_district": "Puri",
            "from_state": "Odisha", "to_state": "Odisha",
            "medicine": "ORS", "quantity": 1150, "units_moved": 1150,
            "urgency": "HIGH", "deadline_days": 4, "estimated_cost_inr": 9200,
            "justification": "Puri flood-belt PHCs drew down ORS after diarrheal caseload; Cuttack still holds surplus.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "approved",
            "whatsapp_language": "or",
            "whatsapp_text": _wa("Puri", "Cuttack", "ORS", 1150, 9200, 4, "HIGH", "or"),
        },
        {
            "id": "TXF_OD_002",
            "from_district": "Cuttack", "to_district": "Puri",
            "from_state": "Odisha", "to_state": "Odisha",
            "medicine": "IVFluids", "quantity": 500,
            "urgency": "CRITICAL", "deadline_days": 3, "estimated_cost_inr": 4000,
            "justification": "Puri faces IVFluids stock-out in 5 days; Cuttack has surplus in Odisha.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "or",
            "whatsapp_text": _wa("Puri", "Cuttack", "IVFluids", 500, 4000, 3, "CRITICAL", "or"),
        },
        {
            "id": "TXF_OD_003",
            "from_district": "Cuttack", "to_district": "Balasore",
            "from_state": "Odisha", "to_state": "Odisha",
            "medicine": "ORS", "quantity": 800,
            "urgency": "HIGH", "deadline_days": 5, "estimated_cost_inr": 6400,
            "justification": "Balasore flood corridor PHCs are below 7-day ORS cover; Cuttack can spare 800 units.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "or",
            "whatsapp_text": _wa("Balasore", "Cuttack", "ORS", 800, 6400, 5, "HIGH", "or"),
        },
        {
            "id": "TXF_OD_004",
            "from_district": "Khordha", "to_district": "Puri",
            "from_state": "Odisha", "to_state": "Odisha",
            "medicine": "Paracetamol", "quantity": 420,
            "urgency": "MEDIUM", "deadline_days": 7, "estimated_cost_inr": 3360,
            "justification": "Fever caseload rising in Puri Sadar; Khordha Jatni PHC has a Paracetamol buffer.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "or",
            "whatsapp_text": _wa("Puri", "Khordha", "Paracetamol", 420, 3360, 7, "MEDIUM", "or"),
        },
        {
            "id": "TXF_RJ_001",
            "from_district": "Jodhpur", "to_district": "Barmer",
            "from_state": "Rajasthan", "to_state": "Rajasthan",
            "medicine": "Artemisinin", "quantity": 900,
            "urgency": "CRITICAL", "deadline_days": 2, "estimated_cost_inr": 7200,
            "justification": "Barmer malaria searches +280% vs baseline; PHC Siwana has a 2-day Artemisinin supply.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "hi",
            "whatsapp_text": _wa("Barmer", "Jodhpur", "Artemisinin", 900, 7200, 2, "CRITICAL", "hi"),
        },
        {
            "id": "TXF_RJ_002",
            "from_district": "Jodhpur", "to_district": "Barmer",
            "from_state": "Rajasthan", "to_state": "Rajasthan",
            "medicine": "ORS", "quantity": 1600,
            "urgency": "HIGH", "deadline_days": 3, "estimated_cost_inr": 12800,
            "justification": "Heat is driving ORS use alongside vector cases in Barmer block; Jodhpur rural PHCs are in surplus.",
            "autonomy_level": "ESCALATE", "status": "pending",
            "whatsapp_language": "hi",
            "whatsapp_text": _wa("Barmer", "Jodhpur", "ORS", 1600, 12800, 3, "HIGH", "hi"),
        },
        {
            "id": "TXF_RJ_003",
            "from_district": "Jaipur", "to_district": "Udaipur",
            "from_state": "Rajasthan", "to_state": "Rajasthan",
            "medicine": "Paracetamol", "quantity": 650,
            "urgency": "MEDIUM", "deadline_days": 6, "estimated_cost_inr": 5200,
            "justification": "Udaipur malaria-watch PHCs need a fever-kit top-up before weekend OPD load.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "pending",
            "whatsapp_language": "hi",
            "whatsapp_text": _wa("Udaipur", "Jaipur", "Paracetamol", 650, 5200, 6, "MEDIUM", "hi"),
        },
        {
            "id": "TXF_RJ_004",
            "from_district": "Jodhpur", "to_district": "Barmer",
            "from_state": "Rajasthan", "to_state": "Rajasthan",
            "medicine": "IVFluids", "quantity": 280, "units_moved": 280,
            "urgency": "HIGH", "deadline_days": 4, "estimated_cost_inr": 2240,
            "justification": "Siwana dehydration admissions rose with heatwave; first IV fluids tranche already dispatched.",
            "autonomy_level": "APPROVE_REQUIRED", "status": "approved",
            "whatsapp_language": "hi",
            "whatsapp_text": _wa("Barmer", "Jodhpur", "IVFluids", 280, 2240, 4, "HIGH", "hi"),
        },
    ]


def demo_alerts() -> list[dict]:
    return [
        {
            "id": "AL_MH_001", "type": "sentinel", "state": "Maharashtra", "district": "Raigad",
            "risk_score": 92, "risk_level": "CRITICAL",
            "message": "Dengue and diarrhea case counts far above IDSP baseline. Iron tablets critically low at Mahad and Poladpur.",
            "timestamp": _ts(8), "ai_source": "mock",
        },
        {
            "id": "AL_MH_002", "type": "coordinator", "state": "Maharashtra", "district": "Raigad",
            "transfer_count": 2,
            "message": "Intra-state plan: Nashik surplus covers Raigad ORS and Iron tablets within 3 days.",
            "timestamp": _ts(7), "ai_source": "mock",
        },
        {
            "id": "AL_MH_003", "type": "pipeline", "state": "Maharashtra",
            "message": "Demo seed loaded for Maharashtra. Click Simulate Outbreak to re-score Raigad with live Gemini.",
            "timestamp": _ts(6), "ai_source": "mock",
        },
        {
            "id": "AL_OD_001", "type": "sentinel", "state": "Odisha", "district": "Puri",
            "risk_score": 88, "risk_level": "CRITICAL",
            "message": "Post-flood diarrheal searches +310% vs baseline. PHC Konark has a 2-day IVFluids supply.",
            "timestamp": _ts(18), "ai_source": "mock",
        },
        {
            "id": "AL_OD_002", "type": "sentinel", "state": "Odisha", "district": "Balasore",
            "risk_score": 71, "risk_level": "HIGH",
            "message": "Flood corridor still wet; ORS offtake at Remuna is 1.8x the 14-day mean.",
            "timestamp": _ts(25), "ai_source": "mock",
        },
        {
            "id": "AL_OD_003", "type": "coordinator", "state": "Odisha", "district": "Puri",
            "transfer_count": 3,
            "message": "Intra-state plan: Cuttack surplus covers Puri IVFluids and Balasore ORS within 5 days.",
            "timestamp": _ts(16), "ai_source": "mock",
        },
        {
            "id": "AL_OD_004", "type": "pipeline", "state": "Odisha",
            "message": "Pipeline complete (Odisha). Sentinel + Coordinator labelled mock after Gemini quota.",
            "timestamp": _ts(15), "ai_source": "mock",
        },
        {
            "id": "AL_OD_005", "type": "approve", "state": "Odisha", "district": "Puri",
            "message": "Approved 1,150 ORS Cuttack → Puri",
            "timestamp": _ts(40),
        },
        {
            "id": "AL_RJ_001", "type": "sentinel", "state": "Rajasthan", "district": "Barmer",
            "risk_score": 86, "risk_level": "CRITICAL",
            "message": "Malaria searches in Rajasthan +280% vs baseline. PHC Siwana has a 2-day Artemisinin supply.",
            "timestamp": _ts(12), "ai_source": "mock",
        },
        {
            "id": "AL_RJ_002", "type": "sentinel", "state": "Rajasthan", "district": "Udaipur",
            "risk_score": 58, "risk_level": "MEDIUM",
            "message": "Malaria-watch fever OPD up in Girwa; Paracetamol days-of-cover slipping below 10.",
            "timestamp": _ts(22), "ai_source": "mock",
        },
        {
            "id": "AL_RJ_003", "type": "coordinator", "state": "Rajasthan", "district": "Barmer",
            "transfer_count": 3,
            "message": "Move 900 Artemisinin courses and 1,600 ORS units from Jodhpur surplus within 48 hours.",
            "timestamp": _ts(10), "ai_source": "mock",
        },
        {
            "id": "AL_RJ_004", "type": "pipeline", "state": "Rajasthan",
            "message": "Pipeline complete (Rajasthan). Heat + vector signals fused for Barmer block.",
            "timestamp": _ts(9), "ai_source": "mock",
        },
        {
            "id": "AL_RJ_005", "type": "approve", "state": "Rajasthan", "district": "Barmer",
            "message": "Approved 280 IVFluids Jodhpur → Barmer",
            "timestamp": _ts(55),
        },
    ]


def _transfer_sig(row: dict) -> tuple:
    return (row.get("from_district"), row.get("to_district"), row.get("medicine"), row.get("status"))


def demo_risk_scores() -> dict[str, dict]:
    """District scores so a cold Render boot still shows a full map, not zeros."""
    def row(**kwargs):
        kwargs.setdefault("ai_source", "mock")
        kwargs.setdefault("ai_model", None)
        return kwargs

    return {
        "Raigad": row(
            district="Raigad", state="Maharashtra", risk_score=92, risk_level="CRITICAL",
            days_to_surge=3, key_medicines_at_risk=["IronTablets", "IVFluids"],
            primary_driver="Rapid surge in dengue and diarrhea cases coupled with critical Iron and IV fluid stock shortages.",
            reasoning="IDSP-style case counts exceed baselines across dengue and diarrhea. Several Raigad PHCs are below 5-day Iron tablet cover.",
            recommended_action="Approve Nashik → Raigad ORS and Iron tablet transfers, then deploy vector-control teams.",
        ),
        "Nashik": row(
            district="Nashik", state="Maharashtra", risk_score=18, risk_level="LOW",
            days_to_surge=21, key_medicines_at_risk=[],
            primary_driver="Surplus ORS and Iron tablet buffer; caseload within baseline.",
            reasoning="Stock days-of-supply remain above 14 days across sample PHCs. Safe donor district for intra-state moves.",
            recommended_action="Hold as surplus donor for Raigad.",
        ),
        "Pune": row(
            district="Pune", state="Maharashtra", risk_score=42, risk_level="MEDIUM",
            days_to_surge=12, key_medicines_at_risk=[],
            primary_driver="Moderate fever OPD; stocks adequate.",
            reasoning="Signals are elevated but not at outbreak thresholds. No transfer required.",
            recommended_action="Monitor weekly IDSP-style counts.",
        ),
        "Thane": row(
            district="Thane", state="Maharashtra", risk_score=48, risk_level="MEDIUM",
            days_to_surge=11, key_medicines_at_risk=["IVFluids"],
            primary_driver="Coastal fever corridor; IV fluids tightening at Murbad.",
            reasoning="Medium risk from seasonal fever. Not yet a donor or a priority receiver.",
            recommended_action="Watch IV fluid days-of-cover.",
        ),
        "Puri": row(
            district="Puri", state="Odisha", risk_score=88, risk_level="CRITICAL",
            days_to_surge=4, key_medicines_at_risk=["ORS", "IVFluids"],
            primary_driver="Post-flood diarrheal surge; PHC Konark has a 2-day IVFluids supply.",
            reasoning="Flood-belt PHCs drew down ORS. Cuttack remains the intra-state surplus donor.",
            recommended_action="Approve remaining Cuttack → Puri IV fluids transfer.",
        ),
        "Cuttack": row(
            district="Cuttack", state="Odisha", risk_score=22, risk_level="LOW",
            days_to_surge=18, key_medicines_at_risk=[],
            primary_driver="Surplus ORS and IV fluids relative to footfall.",
            reasoning="Safe donor for Puri and Balasore flood-corridor PHCs.",
            recommended_action="Keep as Odisha surplus hub.",
        ),
        "Khordha": row(
            district="Khordha", state="Odisha", risk_score=36, risk_level="MEDIUM",
            days_to_surge=14, key_medicines_at_risk=[],
            primary_driver="Paracetamol buffer available for Puri fever OPD.",
            reasoning="Not in outbreak. Can spare Paracetamol without dipping below 10-day cover.",
            recommended_action="Optional top-up to Puri Sadar.",
        ),
        "Balasore": row(
            district="Balasore", state="Odisha", risk_score=71, risk_level="HIGH",
            days_to_surge=6, key_medicines_at_risk=["ORS"],
            primary_driver="Flood corridor still wet; ORS offtake 1.8× the 14-day mean.",
            reasoning="High but secondary to Puri. Cuttack can cover an ORS tranche within 5 days.",
            recommended_action="Keep the Cuttack → Balasore ORS transfer on the board.",
        ),
        "Barmer": row(
            district="Barmer", state="Rajasthan", risk_score=86, risk_level="CRITICAL",
            days_to_surge=2, key_medicines_at_risk=["Artemisinin", "ORS"],
            primary_driver="Malaria searches +280% vs baseline; PHC Siwana has a 2-day Artemisinin supply.",
            reasoning="Vector + heat signals together. Jodhpur is the intra-state surplus donor.",
            recommended_action="Approve Jodhpur → Barmer Artemisinin first.",
        ),
        "Jodhpur": row(
            district="Jodhpur", state="Rajasthan", risk_score=19, risk_level="LOW",
            days_to_surge=20, key_medicines_at_risk=[],
            primary_driver="Rural PHCs hold surplus Artemisinin, ORS, and IV fluids.",
            reasoning="Safe donor for Barmer malaria-watch blocks.",
            recommended_action="Hold as Rajasthan surplus hub.",
        ),
        "Jaipur": row(
            district="Jaipur", state="Rajasthan", risk_score=34, risk_level="MEDIUM",
            days_to_surge=13, key_medicines_at_risk=[],
            primary_driver="Urban fever OPD stable; Paracetamol available for Udaipur top-up.",
            reasoning="Not an outbreak district. Can spare a medium Paracetamol move.",
            recommended_action="Optional Jaipur → Udaipur fever-kit transfer.",
        ),
        "Udaipur": row(
            district="Udaipur", state="Rajasthan", risk_score=58, risk_level="MEDIUM",
            days_to_surge=8, key_medicines_at_risk=["Paracetamol"],
            primary_driver="Malaria-watch fever OPD up in Girwa; Paracetamol cover slipping below 10 days.",
            reasoning="Watch district, not yet critical. Weekend OPD could tighten stocks.",
            recommended_action="Keep the Jaipur → Udaipur transfer pending.",
        ),
    }


def demo_impact() -> dict:
    return {
        "stockout_days_prevented": 24,
        "patients_served": 460,
        "units_redistributed": 1430,
        "warnings_issued": 6,
        "leakage_flagged": 4,
    }


def ensure_demo_feed(state: dict) -> bool:
    """Insert missing demo rows so a cold boot still looks like a live ops board."""
    changed = False
    transfers = state.setdefault("transfers", [])
    known_ids = {row.get("id") for row in transfers}
    known_sigs = {_transfer_sig(row) for row in transfers}
    for row in demo_transfers():
        if row["id"] in known_ids or _transfer_sig(row) in known_sigs:
            continue
        transfers.append(dict(row))
        known_ids.add(row["id"])
        known_sigs.add(_transfer_sig(row))
        changed = True

    alerts = state.setdefault("alerts", [])
    known_alert_ids = {row.get("id") for row in alerts}
    for row in demo_alerts():
        if row.get("id") in known_alert_ids:
            continue
        alerts.append(dict(row))
        known_alert_ids.add(row.get("id"))
        changed = True

    scores = state.setdefault("risk_scores", {})
    for district, row in demo_risk_scores().items():
        existing = scores.get(district)
        if existing and existing.get("risk_score"):
            continue
        scores[district] = dict(row)
        changed = True

    impact = state.setdefault("impact", {})
    if not int(impact.get("units_redistributed") or 0):
        impact.update(demo_impact())
        changed = True
    return changed
