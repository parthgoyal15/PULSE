# PULSE frontend

Next.js dashboard for **PULSE** (PHC Health Intelligence Platform).

Full project docs, architecture, and run instructions live in the repo root:

**[README.md](../../README.md)**

## Dev server

Start the Flask backend first (`python3 main.py` in `pulse/backend`), then:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The API URL is `NEXT_PUBLIC_API_URL` in `.env.local` (default `http://localhost:8000`).
