"""
CMO Copilot and delay-impact analysis.

Numbers for stock-out / patient risk are computed from live PHC stock.
Gemini only writes the CMO-facing brief so the figures cannot be hallucinated.
"""

from __future__ import annotations

import json

from agents.gemini_client import GeminiUnavailable, friendly_error, generate_json, generate_text, mocks_allowed

CONSUMPTION_PER_VISIT = 0.15


def daily_use(phc: dict) -> float:
    return max(1.0, float(phc.get("avg_daily_footfall") or 0) * CONSUMPTION_PER_VISIT)


def days_of_supply(phc: dict, medicine: str) -> float:
    stock = float((phc.get("stock") or {}).get(medicine, 0) or 0)
    return round(stock / daily_use(phc), 1)


def compact_risk(risk: dict) -> dict:
    return {
        "district": risk.get("district"),
        "state": risk.get("state"),
        "risk_score": risk.get("risk_score"),
        "risk_level": risk.get("risk_level"),
        "days_to_surge": risk.get("days_to_surge"),
        "primary_driver": risk.get("primary_driver"),
        "key_medicines_at_risk": risk.get("key_medicines_at_risk"),
        "recommended_action": risk.get("recommended_action"),
    }


def compact_transfer(t: dict) -> dict:
    return {
        "id": t.get("id"),
        "from_district": t.get("from_district"),
        "to_district": t.get("to_district"),
        "from_state": t.get("from_state"),
        "to_state": t.get("to_state"),
        "medicine": t.get("medicine"),
        "quantity": t.get("quantity"),
        "urgency": t.get("urgency"),
        "deadline_days": t.get("deadline_days"),
        "estimated_cost_inr": t.get("estimated_cost_inr"),
        "justification": t.get("justification"),
        "status": t.get("status") or "pending",
        "autonomy_level": t.get("autonomy_level"),
    }


def compact_phc_stock(phcs: list[dict]) -> list[dict]:
    rows = []
    for p in phcs:
        stock = p.get("stock") or {}
        rows.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "district": p.get("district"),
            "block": p.get("block"),
            "footfall": p.get("avg_daily_footfall"),
            "stock": stock,
            "days_of_supply": {med: days_of_supply(p, med) for med in stock},
        })
    return rows


def project_delay(transfer: dict, phcs: list[dict], hours: int = 48) -> dict:
    """Deterministic 48h stock projection for the destination district."""
    medicine = transfer.get("medicine") or "ORS"
    dest = transfer.get("to_district")
    days = max(1, int(hours) / 24)
    receivers = [p for p in phcs if p.get("district") == dest]
    phc_rows = []
    stockout = []
    patients_at_risk = 0

    for p in receivers:
        use = daily_use(p)
        have = float((p.get("stock") or {}).get(medicine, 0) or 0)
        remaining = max(0.0, have - use * days)
        now_days = round(have / use, 1)
        after_days = round(remaining / use, 1)
        hits_zero = remaining <= 0
        uncovered = 0
        if have < use * days:
            uncovered = int(round((use * days - have) / CONSUMPTION_PER_VISIT))
            uncovered = max(0, uncovered)
        row = {
            "phc_id": p.get("id"),
            "phc_name": p.get("name"),
            "block": p.get("block"),
            "stock_now": int(have),
            "days_supply_now": now_days,
            "stock_after": int(remaining),
            "days_supply_after": after_days,
            "hits_zero": hits_zero,
            "uncovered_patient_visits": uncovered,
        }
        phc_rows.append(row)
        if hits_zero:
            stockout.append(row)
            patients_at_risk += uncovered

    current = (transfer.get("urgency") or "MEDIUM").upper()
    if stockout and current in ("MEDIUM", "LOW"):
        recommended = "HIGH"
    elif stockout and current == "HIGH":
        recommended = "CRITICAL"
    elif stockout:
        recommended = "CRITICAL"
    else:
        recommended = current

    return {
        "hours": hours,
        "medicine": medicine,
        "from_district": transfer.get("from_district"),
        "to_district": dest,
        "quantity": transfer.get("quantity"),
        "current_urgency": current,
        "phcs": phc_rows,
        "stockout_phcs": [r["phc_name"] for r in stockout],
        "stockout_count": len(stockout),
        "patients_at_risk": patients_at_risk,
        "recommended_urgency": recommended,
        "recommend_approve_now": bool(stockout) or current == "CRITICAL",
    }


def _mock_delay_brief(facts: dict) -> dict:
    names = ", ".join(facts["stockout_phcs"]) or "no PHC"
    if facts["stockout_count"]:
        brief = (
            f"Waiting {facts['hours']} hours leaves {facts['stockout_count']} "
            f"{facts['to_district']} PHC(s) ({names}) at zero {facts['medicine']}. "
            f"About {facts['patients_at_risk']} patient visits would go uncovered. "
            f"Approve the {facts['from_district']} → {facts['to_district']} move now."
        )
        headline = f"{facts['stockout_count']} PHC(s) stock out if this waits {facts['hours']}h"
    else:
        brief = (
            f"{facts['to_district']} still has {facts['medicine']} cover after {facts['hours']} hours, "
            f"but the surplus at {facts['from_district']} is unused. Approve on the current deadline "
            f"({facts.get('current_urgency')}) rather than waiting."
        )
        headline = f"No immediate stock-out, but delay still burns the deadline"
    return {
        "headline": headline,
        "cmo_brief": brief,
        "recommended_urgency": facts["recommended_urgency"],
        "recommend_approve_now": facts["recommend_approve_now"],
        "ai_source": "mock",
        "ai_model": None,
    }


def delay_brief(facts: dict, lang: str = "en") -> dict:
    lang_line = (
        "Write headline and cmo_brief in Hindi using Devanagari. Keep district names, "
        "medicine names, and numbers in the original script/digits."
        if lang == "hi"
        else "Write headline and cmo_brief in English."
    )
    prompt = f"""You are advising an Indian district CMO on a medicine transfer.

{lang_line}
Use ONLY the numbers in FACTS. Do not invent PHCs, quantities, or patient counts.
Return ONLY valid JSON:
{{
  "headline": "<one short line>",
  "cmo_brief": "<2-4 sentences. Say which PHCs hit zero, how many patient visits are uncovered, and whether to approve now.>",
  "recommended_urgency": "{facts['recommended_urgency']}",
  "recommend_approve_now": {str(facts['recommend_approve_now']).lower()}
}}

FACTS:
{json.dumps(facts, default=str)}
"""
    try:
        data = generate_json(prompt)
        headline = (data.get("headline") or "").strip()
        brief = (data.get("cmo_brief") or "").strip()
        if not headline or not brief:
            mock = _mock_delay_brief(facts)
            headline = headline or mock["headline"]
            brief = brief or mock["cmo_brief"]
        return {
            "headline": headline,
            "cmo_brief": brief,
            "recommended_urgency": data.get("recommended_urgency") or facts["recommended_urgency"],
            "recommend_approve_now": bool(data.get("recommend_approve_now", facts["recommend_approve_now"])),
            "ai_source": data.get("ai_source") or "gemini",
            "ai_model": data.get("ai_model"),
        }
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        mock = _mock_delay_brief(facts)
        mock["ai_error"] = friendly_error(exc)
        return mock


def _mock_ask(question: str, context: dict) -> dict:
    risks = context.get("risks") or []
    pending = [t for t in (context.get("transfers") or []) if t.get("status") == "pending"]
    top = max(risks, key=lambda r: r.get("risk_score") or 0, default=None)
    first = pending[0] if pending else None
    parts = []
    if top:
        parts.append(
            f"{top.get('district')} is {top.get('risk_level')} ({top.get('risk_score')}/100) — "
            f"{top.get('primary_driver') or 'elevated caseload'}."
        )
    if first:
        parts.append(
            f"Approve {first.get('id')} first: {first.get('quantity')} {first.get('medicine')} "
            f"{first.get('from_district')} → {first.get('to_district')} "
            f"({first.get('urgency')}, {first.get('deadline_days')} day deadline)."
        )
    if not parts:
        parts.append("Run Sentinel or Simulate Outbreak so Copilot has live district scores to reason over.")
    return {
        "answer": " ".join(parts),
        "ai_source": "mock",
        "ai_model": None,
    }


def ask_cmo(question: str, context: dict, lang: str = "en") -> dict:
    lang_line = (
        "Answer in Hindi using Devanagari. Keep district names, medicine names, transfer IDs, and numbers unchanged."
        if lang == "hi"
        else "Answer in clear English."
    )
    prompt = f"""You are PULSE Copilot, briefing an Indian district CMO.

{lang_line}
Use ONLY the CONTEXT JSON. Do not invent districts, PHCs, medicines, or transfer IDs.
If the question cannot be answered from context, say what is missing and what button to click (Run Pipeline or Simulate Outbreak).
Keep the answer under 120 words. Be specific: name the transfer id to approve, the medicine, and the destination district.
If asked for an ASHA message, write 4 short WhatsApp lines a field worker can read.

QUESTION:
{question}

CONTEXT:
{json.dumps(context, default=str)}
"""
    try:
        text, source, model = generate_text(prompt)
        return {"answer": text.strip(), "ai_source": source, "ai_model": model}
    except GeminiUnavailable as exc:
        if not mocks_allowed():
            raise
        mock = _mock_ask(question, context)
        mock["ai_error"] = friendly_error(exc)
        return mock
