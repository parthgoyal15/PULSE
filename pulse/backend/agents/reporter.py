"""
Reporter Agent — WhatsApp copy and briefs.

CMO alerts are written in the state's language (Marathi / Odia) plus English.
"""

from __future__ import annotations

import json

from agents.gemini_client import GeminiUnavailable, generate_text, mocks_allowed, friendly_error
from data.mock_phcs import STATE_META, state_for_district

ROLE_TONE = {
    "asha_worker": "Simple Hindi/English mix, encouraging, short bullet points, WhatsApp-friendly",
    "district_cmo": "Professional, analytical, actionable, concise",
    "state_secretary": "Strategic, comparative, policy-oriented, formal",
    "ministry": "Executive brief, national scale, ROI-focused, 3 bullet max",
}


def _language_for_transfer(transfer: dict) -> tuple[str, str]:
    state = transfer.get("to_state") or state_for_district(transfer.get("to_district", ""))
    meta = STATE_META.get(state, {})
    return meta.get("language", "hi"), meta.get("language_name", "Hindi")


async def generate_whatsapp_alert(transfer: dict, recipient_role: str = "district_cmo") -> dict:
    """Return {text, language, ai_source, ai_model}."""
    lang_code, lang_name = _language_for_transfer(transfer)
    prompt = f"""Write a WhatsApp alert for an Indian District CMO ({recipient_role}).

Language: {lang_name} first (4-8 short lines), then a blank line, then a 4-line English summary.
No markdown. No hashtags. Keep under 700 characters.

Transfer JSON:
{json.dumps(transfer, default=str)}

Include: district, risk/urgency, medicine + quantity, from → to, cost, and that they can reply Approve / Modify / Escalate.
"""

    try:
        text, source, model = generate_text(prompt)
        return {"text": text, "language": lang_code, "language_name": lang_name, "ai_source": source, "ai_model": model}
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        return {
            "text": _mock_whatsapp(transfer, lang_code),
            "language": lang_code,
            "language_name": lang_name,
            "ai_source": "mock",
            "ai_model": None,
            "ai_error": friendly_error(exc),
        }


async def generate_weekly_brief(district: str, risk_data: dict, transfers: list) -> dict:
    state = risk_data.get("state") or state_for_district(district)
    prompt = f"""Write a weekly health intelligence brief for the District CMO of {district}, {state}.

Risk Assessment: {json.dumps(risk_data, default=str)}
Pending Transfers: {json.dumps(transfers, default=str)}

Format as a professional report with sections:
1. Executive Summary (2 sentences)
2. Supply Chain Status
3. Demand Forecast — Next 14 Days
4. Staff & Bed Status
5. AI Actions Taken This Week
6. Recommended Actions (numbered list)

Tone: {ROLE_TONE['district_cmo']}
Length: ~300 words. No markdown headers, use ALL CAPS for section titles.
Do not claim BigQuery, Firebase, or live IDSP feeds.
"""
    try:
        text, source, model = generate_text(prompt)
        return {"report": text, "ai_source": source, "ai_model": model}
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        return {
            "report": _mock_weekly_brief(district, state, risk_data),
            "ai_source": "mock",
            "ai_model": None,
            "ai_error": friendly_error(exc),
        }


async def generate_post_incident_report(district: str, incident: dict) -> dict:
    prompt = f"""Write a post-incident analysis for a medicine stock-out.

District: {district}
Incident: {json.dumps(incident, default=str)}

Include: timeline, root cause, what the system predicted, what failed, recommended changes.
Direct. Max 400 words. Do not invent live national datasets.
"""
    try:
        text, source, model = generate_text(prompt)
        return {"report": text, "ai_source": source, "ai_model": model}
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        return {
            "report": _mock_post_incident(district),
            "ai_source": "mock",
            "ai_model": None,
            "ai_error": friendly_error(exc),
        }


def _mock_whatsapp(transfer: dict, lang: str) -> str:
    dest = transfer.get("to_district", "")
    src = transfer.get("from_district", "")
    med = transfer.get("medicine", "")
    qty = transfer.get("quantity", 0)
    cost = transfer.get("estimated_cost_inr", 0)
    days = transfer.get("deadline_days", 3)
    urgency = transfer.get("urgency", "HIGH")

    if lang == "mr":
        local = (
            f"PULSE इशारा — {dest} जिल्हा\n"
            f"धोका: {urgency} | {days} दिवसांत मागणी वाढण्याची शक्यता\n"
            f"प्रस्तावित हस्तांतरण: {qty} युनिट {med}\n"
            f"{src} → {dest} | अंदाजे खर्च ₹{cost:,}\n"
            f"उत्तर द्या: Approve / Modify / Escalate"
        )
    elif lang == "or":
        local = (
            f"PULSE ସତର୍କତା — {dest} ଜିଲ୍ଲା\n"
            f"ବିପଦ: {urgency} | {days} ଦିନ ମଧ୍ୟରେ ଚାହିଦା ବୃଦ୍ଧି\n"
            f"ପ୍ରସ୍ତାବିତ ସ୍ଥାନାନ୍ତର: {qty} ୟୁନିଟ {med}\n"
            f"{src} → {dest} | ଆନୁମାନିକ ଖର୍ଚ୍ଚ ₹{cost:,}\n"
            f"ଉତ୍ତର ଦିଅନ୍ତୁ: Approve / Modify / Escalate"
        )
    else:
        local = (
            f"PULSE चेतावनी — {dest}\n"
            f"जोखिम: {urgency} | {days} दिनों में मांग बढ़ सकती है\n"
            f"{qty} यूनिट {med} · {src} → {dest}\n"
            f"Approve / Modify / Escalate"
        )

    english = (
        f"\n\nEN: {urgency} — move {qty} {med} from {src} to {dest} "
        f"in {days} days (₹{cost:,}). Reply Approve, Modify, or Escalate."
    )
    return local + english


def _mock_weekly_brief(district: str, state: str, risk_data: dict) -> str:
    score = risk_data.get("risk_score", 50)
    return f"""{district.upper()} DISTRICT HEALTH INTELLIGENCE BRIEF
{state} | Generated by PULSE (mock copy — Gemini not live)

EXECUTIVE SUMMARY
{district} currently scores {score}/100. Supply pre-positioning should be reviewed this week at the highest-risk PHCs.

SUPPLY CHAIN STATUS
See pending transfers in the dashboard. Stock figures are from the demo PHC sample, not HMIS.

DEMAND FORECAST — NEXT 14 DAYS
Based on weather + search trends + demo IDSP-style counts fused by the Sentinel agent.

STAFF & BED STATUS
Sample PHC occupancy and attendance are shown on the map popups.

AI ACTIONS TAKEN THIS WEEK
Pipeline runs are labelled Gemini or mock in the dashboard header.

RECOMMENDED ACTIONS
1. Approve pending HIGH/CRITICAL transfers
2. Confirm last-mile dispatch with the block medical officer
3. Re-run Sentinel after the next rainfall update"""


def _mock_post_incident(district: str) -> str:
    return f"""POST-INCIDENT ANALYSIS — {district.upper()} DISTRICT
Demo narrative for judging (not a live event log).

TIMELINE
PULSE elevated risk more than a week before the modelled stock-out window.
A reduced transfer quantity left the index PHC exposed.

ROOT CAUSE
Human modification of a HIGH-confidence recommendation without a recorded justification.

WHAT PULSE GOT RIGHT
Direction of surge and the medicine at risk.

WHAT FAILED
Approve / escalate loop must persist — a refresh must not rewind the decision.

SYSTEM CHANGES RECOMMENDED
1. Require a written reason to cut quantity on CRITICAL transfers
2. Auto-escalate if no action in 48 hours"""
