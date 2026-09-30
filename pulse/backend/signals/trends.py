import asyncio
from typing import Optional

# Symptom keywords in regional languages
SYMPTOM_KEYWORDS = {
    "dengue":   ["dengue", "डेंगू", "डेंग्यू"],
    "diarrhea": ["दस्त", "अतिसार", "diarrhea"],
    "fever":    ["बुखार", "ताप", "fever"],
    "malaria":  ["मलेरिया", "malaria", "हिवताप"],
}

async def get_trends_signal(geo_code: str = "IN-MH") -> dict:
    """
    Pull Google Trends for health symptom keywords.
    Returns normalized signal scores per disease.
    Falls back to mock data if pytrends fails (rate limiting is common).
    """
    try:
        from pytrends.request import TrendReq
        import pandas as pd

        pytrends = TrendReq(hl="hi-IN", tz=330, timeout=(10, 25))
        scores = {}

        for disease, keywords in SYMPTOM_KEYWORDS.items():
            try:
                await asyncio.sleep(1)  # avoid rate limiting
                pytrends.build_payload(
                    keywords[:2],  # max 5, use top 2 per disease
                    geo=geo_code,
                    timeframe="now 30-d",
                )
                df = pytrends.interest_over_time()
                if not df.empty:
                    recent_avg = df[keywords[:2]].iloc[-7:].values.mean()
                    baseline_avg = df[keywords[:2]].iloc[:-7].values.mean()
                    scores[disease] = {
                        "recent_avg": round(float(recent_avg), 1),
                        "baseline_avg": round(float(baseline_avg), 1),
                        "change_pct": round(
                            ((recent_avg - baseline_avg) / max(baseline_avg, 1)) * 100, 1
                        ),
                    }
                else:
                    scores[disease] = _mock_score(disease)
            except Exception:
                scores[disease] = _mock_score(disease)

        return scores

    except ImportError:
        return _mock_trends()


def _mock_score(disease: str) -> dict:
    """Realistic mock scores for development without pytrends."""
    defaults = {
        "dengue":   {"recent_avg": 68.0, "baseline_avg": 20.0, "change_pct": 240.0},
        "diarrhea": {"recent_avg": 45.0, "baseline_avg": 28.0, "change_pct": 60.7},
        "fever":    {"recent_avg": 52.0, "baseline_avg": 35.0, "change_pct": 48.6},
        "malaria":  {"recent_avg": 22.0, "baseline_avg": 18.0, "change_pct": 22.2},
    }
    return defaults.get(disease, {"recent_avg": 30.0, "baseline_avg": 25.0, "change_pct": 20.0})


def _mock_trends() -> dict:
    return {disease: _mock_score(disease) for disease in SYMPTOM_KEYWORDS}


async def get_simulated_outbreak_trends(kind: str = "dengue") -> dict:
    """Inflated trend scores for the cinematic demo (dengue vs flood/diarrhea)."""
    if kind == "flood":
        return {
            "dengue":   {"recent_avg": 28.0, "baseline_avg": 20.0, "change_pct": 40.0},
            "diarrhea": {"recent_avg": 96.0, "baseline_avg": 28.0, "change_pct": 242.9},
            "fever":    {"recent_avg": 74.0, "baseline_avg": 35.0, "change_pct": 111.4},
            "malaria":  {"recent_avg": 31.0, "baseline_avg": 18.0, "change_pct": 72.2},
        }
    if kind == "malaria":
        return {
            "dengue":   {"recent_avg": 24.0, "baseline_avg": 20.0, "change_pct": 20.0},
            "diarrhea": {"recent_avg": 40.0, "baseline_avg": 28.0, "change_pct": 42.9},
            "fever":    {"recent_avg": 88.0, "baseline_avg": 35.0, "change_pct": 151.4},
            "malaria":  {"recent_avg": 91.0, "baseline_avg": 18.0, "change_pct": 405.6},
        }
    return {
        "dengue":   {"recent_avg": 92.0, "baseline_avg": 20.0, "change_pct": 360.0},
        "diarrhea": {"recent_avg": 78.0, "baseline_avg": 28.0, "change_pct": 178.6},
        "fever":    {"recent_avg": 85.0, "baseline_avg": 35.0, "change_pct": 142.9},
        "malaria":  {"recent_avg": 35.0, "baseline_avg": 18.0, "change_pct": 94.4},
    }
