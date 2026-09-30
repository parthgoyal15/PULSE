import httpx
from typing import Optional

async def get_weather_signal(lat: float, lng: float) -> dict:
    """Fetch 14-day rainfall forecast from Open-Meteo (free, no key needed)."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lng}"
            f"&daily=precipitation_sum,temperature_2m_max"
            f"&forecast_days=14&timezone=Asia%2FKolkata"
        )
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()

        rainfall_14d = sum(data["daily"]["precipitation_sum"])
        max_temp_avg = sum(data["daily"]["temperature_2m_max"]) / 14

        # Historical monsoon average for Maharashtra: ~120mm/14d
        # Above 150mm = elevated flood/disease risk
        rainfall_anomaly = max(0, (rainfall_14d - 120) / 120) * 100

        return {
            "rainfall_14d_mm": round(rainfall_14d, 1),
            "max_temp_avg_c": round(max_temp_avg, 1),
            "rainfall_anomaly_pct": round(rainfall_anomaly, 1),
            "monsoon_risk": "HIGH" if rainfall_14d > 200 else "MEDIUM" if rainfall_14d > 120 else "LOW",
        }
    except Exception as e:
        return {
            "rainfall_14d_mm": 85.0,
            "max_temp_avg_c": 31.2,
            "rainfall_anomaly_pct": 0.0,
            "monsoon_risk": "LOW",
            "error": str(e),
        }
