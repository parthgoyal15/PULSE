# PULSE

**Predictive Unified Health Surge Engine** — a PHC health-intelligence platform for India’s Primary Health Centre network.

PULSE was built for the **Code for Community** hackathon, **Track 03: Smart Health & Supply Chain Resilience**. It is a working demo, not a production system.

The idea: detect a dengue or monsoon surge *before* medicines run out, then move surplus stock (ORS, IV fluids, etc.) from a neighbouring district and alert the district CMO on WhatsApp.

The live demo stories:

- **Maharashtra:** Raigad goes critical (dengue), Nashik has surplus, PULSE proposes the transfer. CMO copy is drafted in **Marathi**.
- **Odisha:** Puri goes critical (post-flood diarrhea), Cuttack has surplus. CMO copy is drafted in **Odia**.

Both states share the same Sentinel + Coordinator model. Approve on the dashboard **moves mock stock** and persists in SQLite.

---

## Problem

Public healthcare supply chains cannot see medicine stocks, patient footfall, and outbreak risk in one place. Districts often discover a stock-out after patients are already turned away. Neighbouring PHCs may be sitting on surplus of the same drugs.

## What PULSE does

1. **Sentinel** fuses weather, Google Trends, IDSP-style case counts, and PHC stock into a district risk score. Uses Gemini when `GEMINI_API_KEY` is set; otherwise a **labelled** mock (`ai_source: mock`).
2. **Coordinator** turns those scores into a redistribution plan (prefers intra-state: Nashik→Raigad, Cuttack→Puri).
3. **Reporter** drafts Marathi/Odia WhatsApp alerts plus weekly / post-incident briefs.
4. **Leakage** flags PHCs where reported dispensed volume is far above expected consumption from footfall. Audit / notify buttons persist.

The dashboard shows a national → state → district map, KPIs, risk reasoning, transfer cards, and an agent alert feed. A second page covers reports, 2019 backtesting, leakage, and a WhatsApp phone mock.

---

## Quick start

You need **two terminals**. Backend on port **8000**, frontend on port **3000**.

**Prerequisites:** Python 3.11+ (3.11–3.13 recommended), Node.js 20+, npm.

### 1. Backend

```bash
cd pulse/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional — works without keys
python3 main.py
```

You should see: `PULSE Backend starting on http://localhost:8000`

Check it: open [http://localhost:8000](http://localhost:8000) — JSON like `{"service":"PULSE","status":"online",...}`.

### 2. Frontend

```bash
cd pulse/frontend
npm install
cp .env.example .env.local         # already set to http://localhost:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Keys are optional for a local demo. Without `GEMINI_API_KEY` the dashboard banner says **Google AI is offline** and every score is labelled MOCK. For judging, put a real key in `pulse/backend/.env`. Set `ALLOW_MOCK_AGENTS=false` if you want the API to return 503 instead of mocks.

### Demo walkthrough

1. Dashboard opens on Maharashtra. Header banner shows whether Gemini is live.
2. Click **Simulate Outbreak** — Raigad goes critical; Nashik → Raigad transfers appear; CMO copy is in Marathi + English.
3. Click **Approve** — donor PHC stock decrements, KPIs update, the card stays approved after refresh (SQLite).
4. National view → click **Odisha** → **Simulate Outbreak** — Puri flood/diarrhea, Cuttack surplus, Odia CMO copy.
5. **Reports** (`/reports`) for briefs (labelled Gemini vs mock), 2019 backtesting, leakage (audit/notify persist), WhatsApp preview.

The UI polls every 15 seconds. Transfers and stock survive a backend restart.

### Live demo (cloud)

The public dashboard is the **frontend** URL. The API is a separate service.

1. Push this repo to GitHub (public).
2. On [Render](https://render.com), **New → Blueprint** and select this repo (`render.yaml`).
3. When prompted, paste `GEMINI_API_KEY` (same key as `pulse/backend/.env` locally). Do not commit the key.
4. After both services are live, open the **pulse-web** URL.

Render free instances sleep after idle time. The first load can take 30–60 seconds. **Simulate Outbreak** can take up to a minute (live Gemini) — the service timeout is 180s.

---

## Repository layout

```
CodeForCommunity/
├── README.md                 ← you are here
├── .claude/                  # local Claude Code permissions / curl checks
└── pulse/
    ├── backend/              # Flask API — http://localhost:8000
    │   ├── main.py           # all HTTP routes + in-memory state
    │   ├── agents/           # Sentinel, Coordinator, Reporter, Leakage
    │   ├── signals/          # weather, Google Trends, IDSP
    │   ├── data/             # mock PHCs + 2019 backtesting fixture
    │   ├── whatsapp/         # Cloud API client (demo mode without creds)
    │   ├── requirements.txt
    │   └── .env.example
    └── frontend/             # Next.js App Router — http://localhost:3000
        ├── app/page.tsx      # ops dashboard
        ├── app/reports/page.tsx
        ├── components/       # map, risk, transfers, alerts, reports
        └── lib/              # API client + TypeScript types
```

---

## Tech stack

| State | Tools |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Leaflet |
| Backend | Python, Flask 3, flask-cors, httpx, SQLite |
| AI | Google Gemini (`gemini-3.8-flash`, with fallbacks) via `google-genai` |
| Signals | Open-Meteo (live rainfall), pytrends (often rate-limited), IDSP-style demo counts |
| Messaging | WhatsApp Cloud API when token + phone ID are set; otherwise console demo delivery |

### Environment variables

**Backend** (`pulse/backend/.env`) — copy from `.env.example`:

| Variable | Required? | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | For judging | Free key from [Google AI Studio](https://aistudio.google.com/apikey). Without it, agents return **labelled** mocks. |
| `ALLOW_MOCK_AGENTS` | No | Default `true`. Set `false` to 503 instead of mocks. |
| `WHATSAPP_TOKEN` | No | Meta WhatsApp Cloud API token |
| `WHATSAPP_PHONE_ID` | No | WhatsApp phone number ID |
| `WHATSAPP_VERIFY_TOKEN` | No | Webhook verify token (default `pulse_verify_token_2024`) |
| `CMO_PHONE_MH` / `CMO_PHONE_OD` | No | E.164 numbers (no +) for live WhatsApp |

**Frontend** (`pulse/frontend/.env.local`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Architecture

```
Open-Meteo ──┐
Google Trends┤
Mock IDSP ───┼──► Sentinel (Gemini) ──► district risk scores
Mock stock ──┘                              │
                                            ▼
                                   Coordinator (Gemini)
                                            │
                          transfers + WhatsApp copy (Reporter)
                                            │
                     Flask API ◄────────────┘
                            │
                     Next.js dashboard (poll 15s)
```

**Operational states**

| State | Outbreak | Surplus donor | CMO language |
|---|---|---|---|
| Maharashtra | Raigad dengue | Nashik | Marathi |
| Odisha | Puri flood / diarrhea | Cuttack | Odia |
| Rajasthan | Barmer malaria / heat | Jodhpur | Hindi |

Other Indian states are national markers only. Sample PHCs (not the full `phc_count`) are shown on the map. IDSP-style counts are demo baselines, not a live MoHFW feed.

---

## Features

### Dashboard (`/`)

- National / state / district Leaflet map (OSM tiles)
- KPI strip: stock-out days prevented, patients served, units redistributed, warnings, leakage flagged
- Risk panel with score, Gemini vs mock label, days-to-surge, reasoning
- Transfer cards — Approve moves stock, Escalate / Modify persist in SQLite
- Agent alert feed
- **Run Pipeline** → `POST /run/all?state=`
- **Simulate Outbreak** → `POST /simulate/outbreak?state=Maharashtra` or `Odisha`

### Reports (`/reports`)

| Tab | What you see |
|---|---|
| Weekly brief | Gemini (or canned) brief for a district |
| Monthly overview | Same generator, scoped to a state |
| Post-incident | After-action style report |
| Backtesting | Scripted 2019 Raigad dengue story (16-day early warning, 86× ROI narrative) |
| Leakage | PHCs where dispensed vs footfall looks anomalous (2 PHCs pre-flagged in mock data) |
| WhatsApp demo | Phone mock of CMO approve / escalate flow |

---

## API

Base URL: `http://localhost:8000`

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/status` | Gemini live, WhatsApp live, operational states |
| GET | `/phcs` | Sample PHCs (`?district=` or `?state=`) |
| GET | `/districts` | Districts + latest risk (`?state=`) |
| GET | `/states` | National markers (`operational: true` for MH & Odisha) |
| POST | `/run/all?simulated=&state=` | Sentinel + coordinator for a state (or all) |
| POST | `/simulate/outbreak?state=` | Raigad dengue or Puri flood |
| POST | `/transfers/<id>/approve` | Persist, move stock, bump KPIs |
| POST | `/transfers/<id>/escalate` | Mark escalated |
| POST | `/transfers/<id>/modify` | Body `{quantity, reason}` |
| POST | `/leakage/<phc_id>/audit` | Schedule audit |
| POST | `/leakage/<phc_id>/notify` | Notify block officer |
| GET | `/risk/<district>` | Latest Sentinel score |
| GET | `/transfers` | Current redistribution plan |
| GET | `/alerts` | Last 20 agent alerts |
| GET | `/impact` | KPI counters |
| POST | `/run/sentinel?district=&simulated=` | Score one district |
| POST | `/run/coordinator` | Plan transfers from existing scores |
| POST | `/run/all?simulated=` | Sentinel all districts + coordinator |
| POST | `/simulate/outbreak?state=` | Cinematic outbreak for that state |
| GET | `/backtesting` | 2019 dengue fixture |
| GET | `/leakage` | Leakage flags (`?district=` optional) |
| GET | `/report/weekly/<district>` | Weekly brief |
| GET | `/report/monthly/<state>` | Monthly overview |
| GET | `/report/post-incident/<district>` | Post-incident report |
| GET/POST | `/webhook/whatsapp` | Meta webhook verify + Approve / Escalate |

Quick checks:

```bash
curl http://localhost:8000/status
curl -X POST "http://localhost:8000/simulate/outbreak?state=Odisha"
curl -X POST http://localhost:8000/transfers/TXF_001/approve
```

---

## Agents (backend)

| Agent | File | Job |
|---|---|---|
| Sentinel | `pulse/backend/agents/sentinel.py` | Fuse weather + trends + IDSP + stock → risk JSON |
| Coordinator | `pulse/backend/agents/coordinator.py` | Surplus (score &lt; 25) vs deficit (score &gt; 60) → transfer plan |
| Reporter | `pulse/backend/agents/reporter.py` | WhatsApp template, weekly brief, post-incident copy |
| Leakage | `pulse/backend/agents/leakage.py` | Dispensed vs expected from footfall |

**Signals**

- `signals/weather.py` — Open-Meteo 14-day rainfall vs a 120 mm monsoon baseline; falls back to numbers if the network fails
- `signals/trends.py` — Marathi/English symptom keywords via pytrends; often mocked because of rate limits
- `signals/idsp.py` — Hardcoded baseline vs outbreak case counts (not live IDSP)

---

## Current limitations

Still a **hackathon prototype**:

- Sample PHCs, not a live HMIS feed. IDSP counts are labelled demo baselines.
- National markers besides Maharashtra, Odisha, and Rajasthan do not run the pipeline.
- Map is Leaflet/OSM, not Google Maps. No Vertex AutoML, BigQuery, or Firebase — persistence is SQLite.
- “Graduated autonomy” timers (auto-execute in 1h / 4h) are not scheduled jobs; Approve is explicit.
- Backtesting is a static 2019 narrative.
- No auth, tests, Docker, or CI.

---

## License / context

Built as a Code for Community hackathon submission. Not affiliated with MoHFW, IDSP, or any state health department. All PHC stock, footfall, and 2019 ROI figures are **illustrative mock data**.
