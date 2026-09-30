import os
import copy
import json
import asyncio
import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

load_dotenv()

from data.mock_phcs import (
    MOCK_PHCS, DISTRICTS, NATIONAL_STATES,
    OPERATIONAL_STATES, OUTBREAK_SCENARIO, STATE_META,
    districts_in_state, state_for_district,
)
from data.backtesting import BACKTESTING_2019
from data.demo_feed import ensure_demo_feed
from agents.leakage import detect_leakage
from agents.sentinel import run_sentinel, run_sentinel_many
from agents.coordinator import run_coordinator
from agents.reporter import generate_whatsapp_alert, generate_weekly_brief, generate_post_incident_report
from agents.copilot import (
    ask_cmo,
    compact_phc_stock,
    compact_risk,
    compact_transfer,
    delay_brief,
    project_delay,
)
from agents.gemini_client import (
    GeminiUnavailable,
    friendly_error,
    gemini_configured,
    gemini_live,
    generate_text,
    mocks_allowed,
    quota_blocked,
)
from whatsapp.client import send_alert_message, send_text_message, parse_webhook_event
import store

app = Flask(__name__)
CORS(app)

DEFAULT_IMPACT = {
    "stockout_days_prevented": 0,
    "patients_served": 0,
    "units_redistributed": 0,
    "warnings_issued": 0,
    "leakage_flagged": 0,
}

PHCS: list[dict] = copy.deepcopy(MOCK_PHCS)

_state = {
    "risk_scores": {},
    "transfers": [],
    "alerts": [],
    "impact": dict(DEFAULT_IMPACT),
    "leakage_actions": {},
    "last_ai_error": None,
    "last_ai_source": None,
}


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _run(coro):
    return asyncio.run(coro)


def _persist():
    store.save("state", _state)
    store.save("phcs", PHCS)


def _restore():
    global PHCS, _state
    saved_state = store.load("state", None)
    if saved_state:
        _state.update(saved_state)
        _state.setdefault("impact", dict(DEFAULT_IMPACT))
        _state.setdefault("leakage_actions", {})
    saved_phcs = store.load("phcs", None)
    if saved_phcs and isinstance(saved_phcs, list) and len(saved_phcs) == len(MOCK_PHCS):
        PHCS = saved_phcs
    _state["impact"]["leakage_flagged"] = sum(
        1 for r in detect_leakage() if r["status"] == "FLAGGED"
    )
    _clean_ai_errors()
    ensure_demo_feed(_state)
    _refresh_operational_state_scores()
    _persist()


def _clean_ai_errors():
    last = _state.get("last_ai_error")
    if last:
        _state["last_ai_error"] = friendly_error(last)
    for risk in _state.get("risk_scores", {}).values():
        if isinstance(risk, dict) and risk.get("ai_error"):
            risk["ai_error"] = friendly_error(risk["ai_error"])


def _agent_error(exc: Exception, status=503):
    note = friendly_error(exc)
    _state["last_ai_error"] = note
    _persist()
    return jsonify({
        "error": note,
        "gemini_live": gemini_live(),
        "quota_blocked": quota_blocked(),
        "allow_mocks": mocks_allowed(),
    }), status


def _score_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def _refresh_operational_state_scores():
    for state_name in OPERATIONAL_STATES:
        names = districts_in_state(state_name)
        scores = [_state["risk_scores"][n] for n in names if n in _state["risk_scores"]]
        if not scores:
            continue
        avg = int(round(sum(s.get("risk_score", 0) for s in scores) / len(scores)))
        worst = max(scores, key=lambda s: s.get("risk_score", 0))
        for entry in NATIONAL_STATES:
            if entry["name"] == state_name:
                entry["risk_score"] = avg
                entry["risk_level"] = _score_level(avg)
                entry["primary_driver"] = worst.get("primary_driver", entry.get("primary_driver", ""))
                entry["operational"] = True


def _annotate_states():
    out = []
    for entry in NATIONAL_STATES:
        row = dict(entry)
        row["operational"] = entry["name"] in OPERATIONAL_STATES
        out.append(row)
    return out


def _apply_stock_move(transfer: dict) -> int:
    """Move medicine off donor PHCs onto destination PHCs. Returns units actually moved."""
    medicine = transfer["medicine"]
    remaining = int(transfer["quantity"])
    donors = [p for p in PHCS if p["district"] == transfer["from_district"]]
    donors.sort(key=lambda p: p["stock"].get(medicine, 0), reverse=True)
    moved = 0
    for phc in donors:
        if remaining <= 0:
            break
        have = int(phc["stock"].get(medicine, 0))
        take = min(have, remaining)
        phc["stock"][medicine] = have - take
        remaining -= take
        moved += take

    receivers = [p for p in PHCS if p["district"] == transfer["to_district"]]
    receivers.sort(key=lambda p: p["stock"].get(medicine, 0))
    if receivers and moved:
        each, extra = divmod(moved, len(receivers))
        for i, phc in enumerate(receivers):
            phc["stock"][medicine] = int(phc["stock"].get(medicine, 0)) + each + (1 if i < extra else 0)
    return moved


def _find_transfer(transfer_id: str) -> dict | None:
    return next((t for t in _state["transfers"] if t["id"] == transfer_id), None)


def _cmo_phone(state: str) -> str:
    env_map = {
        "Maharashtra": "CMO_PHONE_MH",
        "Odisha": "CMO_PHONE_OD",
        "Rajasthan": "CMO_PHONE_RJ",
    }
    env_key = env_map.get(state)
    return ((os.getenv(env_key) if env_key else None) or os.getenv("CMO_PHONE") or "919999999999").strip()


def _phc_by_id(phc_id: str) -> dict | None:
    return next((p for p in PHCS if p.get("id") == phc_id), None)


def _push_alert(**kwargs):
    district = kwargs.get("district") or kwargs.get("to_district")
    state = kwargs.get("state")
    if not state and district:
        state = state_for_district(district)
    if state:
        kwargs["state"] = state
    if district:
        kwargs["district"] = district
    kwargs.setdefault("timestamp", _now())
    _state["alerts"].append(kwargs)


def _tagged_transfers() -> list[dict]:
    out = []
    for item in _state.get("transfers") or []:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        row.setdefault("from_state", state_for_district(row.get("from_district", "")))
        row.setdefault("to_state", state_for_district(row.get("to_district", "")))
        out.append(row)
    return out


def _tagged_alerts() -> list[dict]:
    out = []
    for item in _state.get("alerts") or []:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        if not row.get("state") and row.get("district"):
            row["state"] = state_for_district(row["district"])
        out.append(row)
    return out


def _merge_transfers(incoming: list[dict], *, keep_other_than: str | None = None) -> list[dict]:
    existing_by_id = {t["id"]: t for t in _state["transfers"] if t.get("id")}
    merged = []
    used = set()
    for item in incoming:
        row = dict(item)
        row.setdefault("from_state", state_for_district(row.get("from_district", "")))
        row.setdefault("to_state", state_for_district(row.get("to_district", "")))
        prev = existing_by_id.get(row["id"])
        if prev and prev.get("status") in ("approved", "escalated"):
            merged.append(prev)
        else:
            row.setdefault("status", "pending")
            merged.append(row)
        used.add(row["id"])
    for item in _state["transfers"]:
        if item.get("id") in used:
            continue
        dest = item.get("to_state") or state_for_district(item.get("to_district", ""))
        src = item.get("from_state") or state_for_district(item.get("from_district", ""))
        touches = dest == keep_other_than or src == keep_other_than
        if keep_other_than and not touches:
            merged.append(item)
        elif item.get("status") in ("approved", "escalated"):
            merged.append(item)
    return merged


_restore()


# ─── Health & State ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return jsonify({
        "service": "PULSE",
        "status": "online",
        "districts": list(DISTRICTS.keys()),
        "operational_states": OPERATIONAL_STATES,
    })


@app.get("/status")
def get_status():
    _clean_ai_errors()
    whatsapp_live = bool(os.getenv("WHATSAPP_TOKEN") and os.getenv("WHATSAPP_PHONE_ID"))
    return jsonify({
        "gemini_live": gemini_live(),
        "gemini_configured": gemini_configured(),
        "quota_blocked": quota_blocked(),
        "allow_mocks": mocks_allowed(),
        "whatsapp_live": whatsapp_live,
        "persistence": "sqlite",
        "operational_states": OPERATIONAL_STATES,
        "outbreak_targets": OUTBREAK_SCENARIO,
        "state_meta": STATE_META,
        "last_ai_error": _state.get("last_ai_error"),
        "last_ai_source": _state.get("last_ai_source"),
    })


@app.get("/phcs")
def get_phcs():
    district = request.args.get("district")
    state = request.args.get("state")
    phcs = PHCS
    if district:
        phcs = [p for p in phcs if p["district"] == district]
    elif state:
        phcs = [p for p in phcs if p["state"] == state]
    result = []
    for phc in phcs:
        p = copy.deepcopy(phc)
        district_risk = _state["risk_scores"].get(p["district"], {})
        p["district_risk_score"] = district_risk.get("risk_score", 0)
        p["district_risk_level"] = district_risk.get("risk_level", "LOW")
        result.append(p)
    return jsonify(result)


@app.get("/states")
def get_states():
    _refresh_operational_state_scores()
    return jsonify(_annotate_states())


@app.get("/districts")
def get_districts():
    state = request.args.get("state")
    result = []
    for name, info in DISTRICTS.items():
        if state and info["state"] != state:
            continue
        risk = _state["risk_scores"].get(name, {})
        result.append({
            "name": name,
            **info,
            "risk_score": risk.get("risk_score", 0),
            "risk_level": risk.get("risk_level", "LOW"),
            "primary_driver": risk.get("primary_driver", ""),
            "days_to_surge": risk.get("days_to_surge", 30),
        })
    return jsonify(result)


@app.get("/risk/<district>")
def get_district_risk(district):
    if district not in DISTRICTS:
        abort(404, description=f"District '{district}' not found")
    stored = _state["risk_scores"].get(district)
    if stored:
        _clean_ai_errors()
        return jsonify(_state["risk_scores"].get(district) or stored)
    return jsonify({
        "district": district,
        "state": state_for_district(district),
        "risk_score": 0,
        "risk_level": "LOW",
        "primary_driver": "",
        "days_to_surge": 30,
        "key_medicines_at_risk": [],
        "reasoning": "Pipeline has not been run for this district yet.",
        "recommended_action": "Run Pipeline or Simulate Outbreak.",
        "ai_source": None,
    })


@app.get("/transfers")
def get_transfers():
    rows = _tagged_transfers()
    return jsonify({"transfers": rows, "count": len(rows)})


@app.get("/alerts")
def get_alerts():
    rows = _tagged_alerts()
    return jsonify({"alerts": rows[-40:]})


@app.get("/impact")
def get_impact():
    return jsonify(_state["impact"])


# ─── Agent Endpoints ───────────────────────────────────────────────────────────

@app.post("/run/sentinel")
def trigger_sentinel():
    district = request.args.get("district")
    simulated = request.args.get("simulated", "false").lower() == "true"
    if not district or district not in DISTRICTS:
        abort(404, description="District not found")
    kind = OUTBREAK_SCENARIO.get(state_for_district(district), {}).get("kind", "dengue")
    try:
        result = _run(run_sentinel(district, simulated=simulated, outbreak_kind=kind, phcs=PHCS))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    _state["risk_scores"][district] = result
    _state["last_ai_source"] = result.get("ai_source")
    _state["last_ai_error"] = result.get("ai_error")
    _push_alert(
        type="sentinel", district=district,
        state=result.get("state") or state_for_district(district),
        risk_score=result["risk_score"], risk_level=result["risk_level"],
        message=result["primary_driver"],
        ai_source=result.get("ai_source"),
    )
    _persist()
    return jsonify(result)


@app.post("/run/coordinator")
def trigger_coordinator():
    if not _state["risk_scores"]:
        abort(400, description="Run sentinel first")
    try:
        plan = _run(run_coordinator(list(_state["risk_scores"].values())))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    incoming = plan.get("transfers", [])
    _state["transfers"] = _merge_transfers(incoming)
    _state["last_ai_source"] = plan.get("ai_source")
    dest_states = sorted({
        t.get("to_state") or state_for_district(t.get("to_district", ""))
        for t in incoming if t.get("to_district") or t.get("to_state")
    })
    _push_alert(
        type="coordinator",
        message=plan.get("summary", "Redistribution plan generated"),
        transfer_count=len(incoming),
        state=dest_states[0] if len(dest_states) == 1 else None,
        ai_source=plan.get("ai_source"),
    )
    _persist()
    return jsonify(plan)


async def _pipeline(simulated: bool, state: str | None):
    names = districts_in_state(state) if state else list(DISTRICTS.keys())
    kind = OUTBREAK_SCENARIO.get(state or "Maharashtra", {}).get("kind", "dengue")
    simulated_for = set(names) if simulated else set()
    results = await run_sentinel_many(
        names, simulated_for=simulated_for, outbreak_kind=kind, phcs=PHCS
    )
    for r in results:
        _state["risk_scores"][r["district"]] = r
    _state["last_ai_error"] = next((r.get("ai_error") for r in results if r.get("ai_error")), None)
    plan = await run_coordinator(results)
    incoming = plan.get("transfers", [])
    _state["transfers"] = _merge_transfers(incoming, keep_other_than=state)
    _state["last_ai_source"] = plan.get("ai_source") or (results[0].get("ai_source") if results else None)

    alerts_sent = []
    for transfer in _state["transfers"]:
        if transfer.get("status") != "pending":
            continue
        if transfer.get("urgency") in ("CRITICAL", "HIGH"):
            msg = await generate_whatsapp_alert(transfer)
            transfer["whatsapp_text"] = msg.get("text")
            transfer["whatsapp_language"] = msg.get("language")
            dest_state = transfer.get("to_state") or state_for_district(transfer.get("to_district", ""))
            sent = await send_alert_message(_cmo_phone(dest_state), transfer, msg["text"])
            alerts_sent.append({
                "transfer_id": transfer["id"],
                "message": msg["text"],
                "language": msg.get("language"),
                "ai_source": msg.get("ai_source"),
                "delivery": sent.get("status", "sent"),
            })
    return {"risk_scores": {r["district"]: r for r in results}, "plan": plan, "alerts_sent": alerts_sent}


@app.post("/run/all")
def run_full_pipeline():
    simulated = request.args.get("simulated", "false").lower() == "true"
    state = request.args.get("state")
    if state and state not in OPERATIONAL_STATES:
        abort(400, description=f"State '{state}' is not operational")
    try:
        result = _run(_pipeline(simulated, state))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    _push_alert(
        type="pipeline",
        message=f"Pipeline complete ({state or 'all operational states'})",
        state=state,
        ai_source=_state.get("last_ai_source"),
    )
    _persist()
    return jsonify(result)


@app.post("/simulate/outbreak")
def simulate_outbreak():
    state = request.args.get("state") or "Maharashtra"
    if state not in OUTBREAK_SCENARIO:
        abort(400, description="No outbreak scenario for this state")
    target = OUTBREAK_SCENARIO[state]["district"]
    kind = OUTBREAK_SCENARIO[state]["kind"]

    async def _sim():
        names = districts_in_state(state)
        results = await run_sentinel_many(
            names, simulated_for={target}, outbreak_kind=kind, phcs=PHCS
        )
        for r in results:
            _state["risk_scores"][r["district"]] = r
            _push_alert(
                type="sentinel", district=r["district"],
                state=r.get("state") or state,
                risk_score=r["risk_score"], risk_level=r["risk_level"],
                message=r["primary_driver"],
                ai_source=r.get("ai_source"),
            )
        plan = await run_coordinator(results)
        incoming = plan.get("transfers", [])
        _state["transfers"] = _merge_transfers(incoming, keep_other_than=state)
        _state["last_ai_source"] = plan.get("ai_source") or (results[0].get("ai_source") if results else None)
        _state["last_ai_error"] = next((r.get("ai_error") for r in results if r.get("ai_error")), None) or plan.get("ai_error")
        _push_alert(
            type="coordinator",
            message=plan.get("summary", "Redistribution plan generated"),
            transfer_count=len(incoming),
            state=state,
            district=target,
            ai_source=plan.get("ai_source"),
        )
        for transfer in _state["transfers"]:
            if transfer.get("status") != "pending":
                continue
            if transfer.get("urgency") in ("CRITICAL", "HIGH"):
                msg = await generate_whatsapp_alert(transfer)
                transfer["whatsapp_text"] = msg.get("text")
                transfer["whatsapp_language"] = msg.get("language")
                dest_state = transfer.get("to_state") or state_for_district(transfer.get("to_district", ""))
                await send_alert_message(_cmo_phone(dest_state), transfer, msg["text"])
        return plan

    try:
        plan = _run(_sim())
    except GeminiUnavailable as exc:
        return _agent_error(exc)

    _state["impact"]["warnings_issued"] += 1
    _state["impact"]["stockout_days_prevented"] += 4
    _refresh_operational_state_scores()
    _persist()

    return jsonify({
        "status": "outbreak_simulated",
        "state": state,
        "affected_district": target,
        "kind": kind,
        "risk_score": _state["risk_scores"].get(target, {}).get("risk_score"),
        "transfers_generated": len(plan.get("transfers", [])),
        "ai_source": _state.get("last_ai_source"),
    })


# ─── Transfers (Approve closes the loop) ───────────────────────────────────────

@app.post("/transfers/<transfer_id>/approve")
def approve_transfer(transfer_id):
    transfer = _find_transfer(transfer_id)
    if not transfer:
        abort(404, description="Transfer not found")
    if transfer.get("status") == "approved":
        return jsonify(transfer)

    moved = _apply_stock_move(transfer)
    transfer["status"] = "approved"
    transfer["approved_at"] = _now()
    transfer["units_moved"] = moved
    _state["impact"]["units_redistributed"] += moved
    _state["impact"]["patients_served"] += int(moved * 0.4)
    dest_state = transfer.get("to_state") or state_for_district(transfer.get("to_district", ""))
    _run(send_text_message(
        _cmo_phone(dest_state),
        f"Approved. {moved} units {transfer['medicine']} dispatching "
        f"{transfer['from_district']} → {transfer['to_district']}. Logged in PULSE SQLite audit.",
    ))
    _push_alert(
        type="approve",
        message=f"Approved {moved} {transfer['medicine']} {transfer['from_district']} → {transfer['to_district']}",
        district=transfer.get("to_district"),
        state=transfer.get("to_state") or state_for_district(transfer.get("to_district", "")),
    )
    _persist()
    return jsonify(transfer)


@app.post("/transfers/<transfer_id>/escalate")
def escalate_transfer(transfer_id):
    transfer = _find_transfer(transfer_id)
    if not transfer:
        abort(404, description="Transfer not found")
    transfer["status"] = "escalated"
    transfer["escalated_at"] = _now()
    dest_state = transfer.get("to_state") or state_for_district(transfer.get("to_district", ""))
    _run(send_text_message(
        _cmo_phone(dest_state),
        f"Escalated to State Health Secretary: {transfer['quantity']} {transfer['medicine']} "
        f"{transfer['from_district']} → {transfer['to_district']}.",
    ))
    _push_alert(
        type="escalate",
        message=f"Escalated {transfer['id']} to state secretary",
        district=transfer.get("to_district"),
        state=transfer.get("to_state") or state_for_district(transfer.get("to_district", "")),
    )
    _persist()
    return jsonify(transfer)


@app.post("/transfers/<transfer_id>/modify")
def modify_transfer(transfer_id):
    transfer = _find_transfer(transfer_id)
    if not transfer:
        abort(404, description="Transfer not found")
    body = request.get_json(silent=True) or {}
    qty = body.get("quantity")
    if qty is not None:
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            abort(400, description="quantity must be an integer")
        if qty <= 0:
            abort(400, description="quantity must be positive")

        old_qty = int(transfer.get("quantity") or 0)
        old_cost = int(transfer.get("estimated_cost_inr") or 0)
        transfer["quantity"] = qty
        # Keep cost proportional to quantity so the card never shows a stale
        # total after a CMO shrinks or grows the requested amount.
        if old_qty > 0 and old_cost > 0:
            transfer["estimated_cost_inr"] = max(1, round(old_cost * qty / old_qty))
        transfer["autonomy_level"] = "AUTO" if qty < 100 else "APPROVE_REQUIRED" if qty <= 1000 else "ESCALATE"

        # The WhatsApp draft quotes the old quantity/cost verbatim — regenerate
        # it so the CMO-facing text always matches the numbers on screen.
        try:
            msg = _run(generate_whatsapp_alert(transfer))
            transfer["whatsapp_text"] = msg.get("text")
            transfer["whatsapp_language"] = msg.get("language")
        except GeminiUnavailable:
            pass  # keep prior draft rather than fail the modify action

    transfer["status"] = "pending"
    transfer["modified_at"] = _now()
    transfer["modify_reason"] = body.get("reason") or "CMO modified quantity"
    _push_alert(
        type="modify",
        message=f"Modified {transfer['id']} to {transfer['quantity']} {transfer['medicine']}",
        district=transfer.get("to_district"),
        state=transfer.get("to_state") or state_for_district(transfer.get("to_district", "")),
    )
    _persist()
    return jsonify(transfer)


# ─── Reports ──────────────────────────────────────────────────────────────────

@app.get("/backtesting")
def get_backtesting():
    return jsonify(BACKTESTING_2019)


@app.get("/leakage")
def get_leakage():
    district = request.args.get("district")
    results = detect_leakage()
    actions = _state.get("leakage_actions") or {}
    for row in results:
        extra = actions.get(row["phc_id"], {})
        row["audit_scheduled"] = bool(extra.get("audit_scheduled"))
        row["officer_notified"] = bool(extra.get("officer_notified"))
        row["action_note"] = extra.get("note")
    if district:
        results = [r for r in results if r["district"] == district]
    return jsonify({
        "leakage_analysis": results,
        "flagged_count": sum(1 for r in results if r["status"] == "FLAGGED"),
    })


@app.post("/leakage/<phc_id>/audit")
def schedule_audit(phc_id):
    actions = _state.setdefault("leakage_actions", {})
    rec = actions.setdefault(phc_id, {})
    rec["audit_scheduled"] = True
    rec["audit_at"] = _now()
    rec["note"] = "Physical audit scheduled with block medical officer"
    phc = _phc_by_id(phc_id)
    _push_alert(
        type="leakage",
        message=f"Physical audit scheduled for {phc_id}",
        district=(phc or {}).get("district"),
        state=(phc or {}).get("state"),
    )
    _persist()
    return jsonify({"phc_id": phc_id, **rec})


@app.post("/leakage/<phc_id>/notify")
def notify_officer(phc_id):
    actions = _state.setdefault("leakage_actions", {})
    rec = actions.setdefault(phc_id, {})
    rec["officer_notified"] = True
    rec["notified_at"] = _now()
    rec["note"] = rec.get("note") or "Block officer notified"
    _run(send_text_message(
        _cmo_phone("Maharashtra"),
        f"PULSE leakage flag: {phc_id} needs block-officer review. Dispensed vs footfall is anomalous.",
    ))
    phc = _phc_by_id(phc_id)
    _push_alert(
        type="leakage",
        message=f"Block officer notified for {phc_id}",
        district=(phc or {}).get("district"),
        state=(phc or {}).get("state"),
    )
    _persist()
    return jsonify({"phc_id": phc_id, **rec})


_TRANSLATION_CACHE: dict[tuple[str, str], dict] = {}
_LANG_NAMES = {"hi": "Hindi"}


@app.post("/translate")
def translate_text():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    target = (body.get("target") or "hi").strip().lower()

    if not text:
        return jsonify({"error": "text is required"}), 400
    if target == "en":
        return jsonify({"translated": text, "ai_source": "original", "ai_model": None})

    lang_name = _LANG_NAMES.get(target, target)
    cache_key = (text, target)
    if cache_key in _TRANSLATION_CACHE:
        return jsonify(_TRANSLATION_CACHE[cache_key])

    prompt = (
        f"Translate the following India public-health text into {lang_name} using "
        "Devanagari script. Keep district names, medicine names, and numbers unchanged. "
        "Return ONLY the translated text — no preamble, no quotes, no explanation.\n\n"
        f"TEXT:\n{text}"
    )
    try:
        translated, ai_source, ai_model = generate_text(prompt)
        result = {"translated": translated.strip(), "ai_source": ai_source, "ai_model": ai_model}
    except GeminiUnavailable as exc:
        result = {
            "translated": text,
            "ai_source": "mock",
            "ai_model": None,
            "ai_error": friendly_error(exc),
        }
    _TRANSLATION_CACHE[cache_key] = result
    return jsonify(result)


def _copilot_context(state: str | None, district: str | None) -> dict:
    risks = list((_state.get("risk_scores") or {}).values())
    if district:
        risks = [r for r in risks if r.get("district") == district]
    elif state:
        risks = [r for r in risks if r.get("state") == state]

    transfers = _tagged_transfers()
    if district:
        transfers = [t for t in transfers if t.get("to_district") == district or t.get("from_district") == district]
    elif state:
        transfers = [t for t in transfers if t.get("to_state") == state or t.get("from_state") == state]

    dests = {t.get("to_district") for t in transfers if t.get("to_district")}
    dests |= {r.get("district") for r in risks if r.get("district")}
    phcs = [p for p in PHCS if p.get("district") in dests] if dests else [
        p for p in PHCS if (not state or p.get("state") == state)
    ]

    alerts = _tagged_alerts()[-8:]
    if district:
        alerts = [a for a in alerts if a.get("district") == district]
    elif state:
        alerts = [a for a in alerts if a.get("state") == state]

    return {
        "scope": {"state": state, "district": district},
        "impact": _state.get("impact"),
        "risks": [compact_risk(r) for r in risks if isinstance(r, dict)],
        "transfers": [compact_transfer(t) for t in transfers],
        "destination_phcs": compact_phc_stock(phcs[:16]),
        "recent_alerts": [
            {"type": a.get("type"), "district": a.get("district"), "message": a.get("message")}
            for a in alerts[-6:]
        ],
    }


_ASK_CACHE: dict[tuple, dict] = {}
_DELAY_CACHE: dict[tuple, dict] = {}


@app.post("/ask")
def ask_copilot():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) > 500:
        return jsonify({"error": "question is too long"}), 400

    state = (body.get("state") or "").strip() or None
    district = (body.get("district") or "").strip() or None
    lang = (body.get("lang") or "en").strip().lower()
    if lang not in ("en", "hi"):
        lang = "en"

    context = _copilot_context(state, district)
    cache_key = (
        question.lower(),
        state,
        district,
        lang,
        json.dumps(context.get("impact"), sort_keys=True, default=str),
        json.dumps([(t.get("id"), t.get("status"), t.get("quantity")) for t in context["transfers"]], default=str),
        json.dumps([(r.get("district"), r.get("risk_score")) for r in context["risks"]], default=str),
    )
    if cache_key in _ASK_CACHE:
        return jsonify(_ASK_CACHE[cache_key])

    try:
        result = ask_cmo(question, context, lang=lang)
    except GeminiUnavailable as exc:
        return _agent_error(exc)

    payload = {
        "question": question,
        "answer": result.get("answer"),
        "ai_source": result.get("ai_source"),
        "ai_model": result.get("ai_model"),
        "ai_error": result.get("ai_error"),
        "scope": context["scope"],
    }
    _ASK_CACHE[cache_key] = payload
    return jsonify(payload)


@app.post("/transfers/<transfer_id>/delay-impact")
def transfer_delay_impact(transfer_id):
    transfer = _find_transfer(transfer_id)
    if not transfer:
        abort(404, description="Transfer not found")

    body = request.get_json(silent=True) or {}
    try:
        hours = int(body.get("hours") or request.args.get("hours") or 48)
    except (TypeError, ValueError):
        abort(400, description="hours must be an integer")
    if hours not in (24, 48, 72):
        hours = 48
    lang = (body.get("lang") or request.args.get("lang") or "en").strip().lower()
    if lang not in ("en", "hi"):
        lang = "en"

    facts = project_delay(transfer, PHCS, hours=hours)
    cache_key = (
        transfer_id,
        hours,
        lang,
        transfer.get("quantity"),
        transfer.get("status"),
        json.dumps(facts["phcs"], sort_keys=True, default=str),
    )
    if cache_key in _DELAY_CACHE:
        return jsonify(_DELAY_CACHE[cache_key])

    try:
        brief = delay_brief(facts, lang=lang)
    except GeminiUnavailable as exc:
        return _agent_error(exc)

    payload = {
        **facts,
        "transfer_id": transfer_id,
        "headline": brief.get("headline"),
        "cmo_brief": brief.get("cmo_brief"),
        "recommended_urgency": brief.get("recommended_urgency") or facts["recommended_urgency"],
        "recommend_approve_now": brief.get("recommend_approve_now", facts["recommend_approve_now"]),
        "ai_source": brief.get("ai_source"),
        "ai_model": brief.get("ai_model"),
        "ai_error": brief.get("ai_error"),
    }
    _DELAY_CACHE[cache_key] = payload
    return jsonify(payload)


@app.get("/report/weekly/<district>")
def weekly_report(district):
    if district not in DISTRICTS:
        abort(404)
    risk = _state["risk_scores"].get(district, {"district": district, "state": state_for_district(district), "risk_score": 30})
    try:
        payload = _run(generate_weekly_brief(district, risk, _state["transfers"]))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    return jsonify({"district": district, **payload})


@app.get("/report/monthly/<state>")
def monthly_report(state):
    names = districts_in_state(state) if state in OPERATIONAL_STATES else list(DISTRICTS.keys())
    scores = [_state["risk_scores"][n] for n in names if n in _state["risk_scores"]]
    summary = scores[0] if scores else {"district": state, "state": state, "risk_score": 50, "risk_level": "MEDIUM"}
    try:
        payload = _run(generate_weekly_brief(state, summary, _state["transfers"]))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    return jsonify({
        "state": state,
        **payload,
        "districts_count": len(names),
        "phcs_count": sum(1 for p in PHCS if p["state"] == state) if state in OPERATIONAL_STATES else len(PHCS),
    })


@app.get("/report/post-incident/<district>")
def post_incident_report(district):
    try:
        payload = _run(generate_post_incident_report(
            district, {"duration_days": 4, "patients_affected": 340}
        ))
    except GeminiUnavailable as exc:
        return _agent_error(exc)
    return jsonify({"district": district, **payload})


# ─── WhatsApp Webhook ─────────────────────────────────────────────────────────

@app.get("/webhook/whatsapp")
def whatsapp_verify():
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "pulse_verify_token_2024")
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge", "")
    abort(403)


@app.post("/webhook/whatsapp")
def whatsapp_webhook():
    body = request.get_json()
    event = parse_webhook_event(body)
    if not event:
        return jsonify({"status": "ignored"})

    button_id = event.get("button_id", "")
    phone = event.get("phone", "")

    if button_id.startswith("approve_"):
        transfer_id = button_id.replace("approve_", "")
        transfer = _find_transfer(transfer_id)
        if transfer:
            moved = _apply_stock_move(transfer)
            transfer["status"] = "approved"
            transfer["units_moved"] = moved
            _state["impact"]["units_redistributed"] += moved
            _persist()
            _run(send_text_message(
                phone,
                f"Approved. {moved} units {transfer['medicine']} dispatching to {transfer['to_district']}.",
            ))
    elif button_id.startswith("escalate_"):
        transfer_id = button_id.replace("escalate_", "")
        transfer = _find_transfer(transfer_id)
        if transfer:
            transfer["status"] = "escalated"
            _persist()
        _run(send_text_message(phone, "Escalated to State Health Secretary."))
    elif event.get("text"):
        _run(send_text_message(phone, _handle_query(event["text"])))

    return jsonify({"status": "processed"})


def _handle_query(text: str) -> str:
    text_lower = text.lower()
    if "risk" in text_lower or "status" in text_lower:
        emoji_map = {"LOW": "GREEN", "MEDIUM": "YELLOW", "HIGH": "RED", "CRITICAL": "CRITICAL"}
        lines = [
            f"{emoji_map.get(r.get('risk_level', 'LOW'), '')} {d}: {r.get('risk_score', 0)}/100"
            for d, r in _state["risk_scores"].items()
        ]
        return "PULSE District Risk:\n" + "\n".join(lines) if lines else "No data yet."
    if "transfer" in text_lower and _state["transfers"]:
        t = _state["transfers"][0]
        return f"{t.get('status', 'pending')}: {t['quantity']} {t['medicine']} · {t['from_district']} → {t['to_district']} ({t['urgency']})"
    return "Reply 'risk status' or 'transfers' for updates."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"\nPULSE Backend starting on http://0.0.0.0:{port}")
    print(f"  Gemini live: {gemini_live()}  |  mocks allowed: {mocks_allowed()}  |  sqlite: {store.DB_PATH}\n")
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "true").lower() in ("1", "true", "yes"))
