"""
IDSP-style weekly case counts.

These are authored demo baselines (not a live pull from idsp.mohfw.gov.in).
The signal payload is labelled so the UI does not claim a live MoHFW feed.
"""

IDSP_BASELINE = {
    "Raigad":   {"dengue": 3,  "diarrhea": 12, "fever_und": 28, "malaria": 2},
    "Pune":     {"dengue": 8,  "diarrhea": 22, "fever_und": 45, "malaria": 1},
    "Nashik":   {"dengue": 2,  "diarrhea": 8,  "fever_und": 18, "malaria": 1},
    "Thane":    {"dengue": 5,  "diarrhea": 15, "fever_und": 32, "malaria": 3},
    "Puri":     {"dengue": 2,  "diarrhea": 18, "fever_und": 24, "malaria": 4},
    "Cuttack":  {"dengue": 3,  "diarrhea": 10, "fever_und": 16, "malaria": 2},
    "Khordha":  {"dengue": 4,  "diarrhea": 14, "fever_und": 20, "malaria": 3},
    "Balasore": {"dengue": 2,  "diarrhea": 16, "fever_und": 22, "malaria": 5},
    "Barmer":   {"dengue": 1,  "diarrhea": 9,  "fever_und": 20, "malaria": 8},
    "Jodhpur":  {"dengue": 3,  "diarrhea": 11, "fever_und": 24, "malaria": 4},
    "Jaipur":   {"dengue": 6,  "diarrhea": 14, "fever_und": 30, "malaria": 2},
    "Udaipur":  {"dengue": 2,  "diarrhea": 10, "fever_und": 18, "malaria": 6},
}

IDSP_OUTBREAK = {
    "Raigad":   {"dengue": 34, "diarrhea": 67, "fever_und": 112, "malaria": 8},
    "Pune":     {"dengue": 12, "diarrhea": 31, "fever_und": 58,  "malaria": 2},
    "Nashik":   {"dengue": 3,  "diarrhea": 9,  "fever_und": 21,  "malaria": 1},
    "Thane":    {"dengue": 18, "diarrhea": 42, "fever_und": 78,  "malaria": 5},
    "Puri":     {"dengue": 6,  "diarrhea": 94, "fever_und": 88,  "malaria": 7},
    "Cuttack":  {"dengue": 4,  "diarrhea": 14, "fever_und": 19,  "malaria": 2},
    "Khordha":  {"dengue": 5,  "diarrhea": 28, "fever_und": 36,  "malaria": 3},
    "Balasore": {"dengue": 5,  "diarrhea": 51, "fever_und": 60,  "malaria": 8},
    "Barmer":   {"dengue": 2,  "diarrhea": 14, "fever_und": 48, "malaria": 41},
    "Jodhpur":  {"dengue": 4,  "diarrhea": 12, "fever_und": 26, "malaria": 5},
    "Jaipur":   {"dengue": 8,  "diarrhea": 16, "fever_und": 34, "malaria": 3},
    "Udaipur":  {"dengue": 3,  "diarrhea": 13, "fever_und": 28, "malaria": 12},
}


def get_idsp_signal(district: str, simulated: bool = False) -> dict:
    source = IDSP_OUTBREAK if simulated else IDSP_BASELINE
    data = source.get(district, {"dengue": 0, "diarrhea": 0, "fever_und": 0, "malaria": 0})
    baseline = IDSP_BASELINE.get(district, data)

    return {
        "source": "idsp_demo_baseline",
        "note": "Demo case counts modelled on IDSP weekly format — not a live MoHFW pull",
        "cases_this_week": data,
        "baseline_cases": baseline,
        "alert_diseases": [
            d for d, count in data.items()
            if count > baseline.get(d, 0) * 2
        ],
    }
