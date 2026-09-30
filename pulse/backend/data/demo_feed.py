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


def ensure_demo_feed(state: dict) -> bool:
    """Insert missing Odisha/Rajasthan demo rows. Returns True if state changed."""
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
    return changed
