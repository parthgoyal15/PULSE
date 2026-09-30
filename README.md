# PULSE

**Predictive Unified Health Surge Engine** — health-intelligence for India’s Primary Health Centre (PHC) network.

Built for **Code for Community**, **Track 03: Smart Health & Supply Chain Resilience**.

**Live demo:** [https://pulse-web-ahao.onrender.com](https://pulse-web-ahao.onrender.com)

Detect a dengue, flood, or malaria surge *before* medicines run out. Move surplus stock from a neighbouring district. Draft the district CMO alert on WhatsApp in the state’s language. Approve on the dashboard **moves mock stock**.

---

## Problem

PHC supply chains cannot see stock, footfall, and outbreak risk in one place. Districts often learn of a stock-out after patients are turned away, while a neighbouring district is sitting on surplus of the same drugs.

## What it does

| Agent | Role |
|---|---|
| **Sentinel** | Fuses weather, search trends, IDSP-style case counts, and PHC stock into a district risk score (Gemini when live; otherwise labelled mock). |
| **Coordinator** | Turns scores into an intra-state redistribution plan (Nashik→Raigad, Cuttack→Puri, Jodhpur→Barmer). |
| **Reporter** | Drafts Marathi / Odia / Hindi WhatsApp copy plus weekly and post-incident briefs. |
| **Copilot** | Answers CMO questions from live board state. Transfer cards can project **if delayed 48 hours**. |
| **Leakage** | Flags PHCs where dispensed volume is far above expected use from footfall. |

### Demo stories

| State | Outbreak | Surplus donor | CMO language |
|---|---|---|---|
| Maharashtra | Raigad dengue | Nashik | Marathi |
| Odisha | Puri flood / diarrhea | Cuttack | Odia |
| Rajasthan | Barmer malaria / heat | Jodhpur | Hindi |

Other states on the national map are markers only.

---

## AI

PULSE uses **Google Gemini** (`google-genai`) for every reasoning and writing step. Lite models are tried first (`gemini-2.5-flash-lite`, `gemini-flash-lite-latest`), then `gemini-2.5-flash` and `gemini-3.8-flash` if needed.

Every Gemini response is tagged **`ai_source: gemini`** or **`ai_source: mock`**. The dashboard shows that label — it never silently fakes Google AI.

| Capability | What Gemini does |
|---|---|
| Sentinel | District risk score, driver, days-to-surge, recommended action |
| Coordinator | Intra-state transfer plan (medicine, quantity, urgency, cost, justification) |
| Reporter | CMO WhatsApp in Marathi / Odia / Hindi + English; weekly, monthly, and post-incident briefs |
| Copilot | Answers CMO questions using current risk, transfers, and PHC stock only |
| Delay analysis | CMO brief for “if this transfer waits 48 hours” (stock-out numbers are calculated in code; Gemini writes the brief) |
| Translate | English ↔ Hindi (Devanagari) for Risk / Transfers / Alerts |

**Not Gemini:** map tiles (OpenStreetMap), leakage flags (rule-based dispensed vs footfall), and read-aloud (device speech synthesis).

---

## Features

### Operations dashboard

- National → state → district **Leaflet map** with risk colouring
- **KPI strip:** stock-out days prevented, patients served, units redistributed, warnings, leakage flagged
- **Risk panel:** score, days-to-surge, medicines at risk, reasoning, recommended action
- **Transfers:** Approve (moves mock stock), Modify quantity, Escalate to state
- **If delayed 48h:** which destination PHCs hit zero stock and uncovered visits
- **Alert feed** from Sentinel / Coordinator / Approve
- **CMO Copilot** with suggested questions, grounded in live board state
- **EN / हिं** view language plus speaker (read-aloud)
- **Run Pipeline** (re-score + re-plan) and **Simulate Outbreak** (live Gemini re-score for the active state)
- Graduated autonomy labels: AUTO / APPROVE REQUIRED / ESCALATE by quantity

### Reports & intelligence (`/reports`)

- Weekly district brief and monthly state overview
- Post-incident analysis
- 2019 Raigad dengue **backtesting** narrative (early-warning story)
- **Leakage detection** with schedule-audit and notify-officer
- **WhatsApp demo** (phone mock of CMO Approve / Modify / Escalate)

### Supply chain behaviour

- Prefers **intra-state** moves; inter-state only if the destination state has no surplus district
- Approve drains donor PHCs (highest stock first) and tops up receiver PHCs (lowest stock first)
- State-language WhatsApp draft on each transfer (Marathi, Odia, or Hindi) plus an English block
- Demo corridors: Maharashtra (Raigad–Nashik), Odisha (Puri–Cuttack), Rajasthan (Barmer–Jodhpur)

---

## Try it (judges)

Open **[pulse-web-ahao.onrender.com](https://pulse-web-ahao.onrender.com)**. The board is already seeded — you do **not** need Simulate Outbreak.

1. Maharashtra map → **Raigad** (critical) → **Transfers** → Nashik → Raigad.
2. **If delayed 48h** on a pending card, then **Approve** (stock and KPIs update).
3. **CMO Copilot** — tap a suggested question.
4. **Reports** → Leakage Detection and WhatsApp Demo.
5. Switch state to Odisha or Rajasthan for the other corridors.

Gemini vs mock is labelled on the risk panel. EN / हिं toggles readable copy and read-aloud.

The first load after idle can take about a minute (free hosting). After that the dashboard is live.

---

## Architecture

```
Open-Meteo ──┐
Search trends┤
IDSP-style ──┼──► Sentinel (Gemini) ──► district risk
PHC stock  ──┘                              │
                                            ▼
                                   Coordinator (Gemini)
                                            │
                          transfers + vernacular WhatsApp
                                            │
                              Flask API  →  Next.js dashboard
```

| Layer | Stack |
|---|---|
| UI | Next.js, TypeScript, Leaflet |
| API | Python, Flask, SQLite |
| AI | Google Gemini (Flash Lite → Flash fallbacks); labelled mock if quota/key is missing |
| Hosting | Render (`pulse-web` + `pulse-api`) |

---

## Scope of this demo

Illustrative PHC stock and IDSP-style counts — not a live HMIS or MoHFW feed. Sample PHCs are shown on the map, not every facility in `phc_count`. Approve is explicit (no background auto-execute timers). Backtesting is a 2019 Raigad narrative used to explain early warning, not a live model replay.

Not affiliated with MoHFW, IDSP, or any state health department.

---

## Run locally

```bash
# API — http://localhost:8000
cd pulse/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # optional GEMINI_API_KEY
python3 main.py

# UI — http://localhost:3000
cd pulse/frontend
npm install && npm run dev
```
