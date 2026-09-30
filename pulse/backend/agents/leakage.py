"""
Medicine Leakage Detection Agent
Compares reported stock dispensed vs expected consumption based on patient footfall.
Flags PHCs where the ratio is anomalous (potential diversion).
"""

from data.mock_phcs import MOCK_PHCS

# Expected ORS packets per patient visit (based on disease type and historical average)
AVG_CONSUMPTION_PER_PATIENT = {
    "ORS": 0.35,
    "Paracetamol": 0.65,
    "IronTablets": 0.20,
    "IVFluids": 0.08,
    "Artemisinin": 0.05,
}

# Simulated "reported dispensed" data (would come from HMIS in production)
REPORTED_DISPENSED = {
    "PHC_RG_001": {"ORS": 142, "Paracetamol": 89, "IronTablets": 38, "IVFluids": 12, "Artemisinin": 6},
    "PHC_RG_002": {"ORS": 1480, "Paracetamol": 95, "IronTablets": 22, "IVFluids": 8,  "Artemisinin": 4},  # ANOMALOUS — ORS 4x expected
    "PHC_RG_003": {"ORS": 198, "Paracetamol": 167, "IronTablets": 71, "IVFluids": 34, "Artemisinin": 18},
    "PHC_RG_004": {"ORS": 127, "Paracetamol": 58, "IronTablets": 18, "IVFluids": 15, "Artemisinin": 9},
    "PHC_PN_001": {"ORS": 298, "Paracetamol": 410, "IronTablets": 112, "IVFluids": 56, "Artemisinin": 28},
    "PHC_PN_002": {"ORS": 187, "Paracetamol": 220, "IronTablets": 84, "IVFluids": 38, "Artemisinin": 15},
    "PHC_PN_003": {"ORS": 412, "Paracetamol": 91, "IronTablets": 1300, "IVFluids": 22, "Artemisinin": 11},  # IRON ANOMALY — ~4.7x expected
    "PHC_NK_001": {"ORS": 138, "Paracetamol": 124, "IronTablets": 52, "IVFluids": 28, "Artemisinin": 14},
    "PHC_NK_002": {"ORS": 97,  "Paracetamol": 88,  "IronTablets": 39, "IVFluids": 19, "Artemisinin": 8},
    "PHC_NK_003": {"ORS": 118, "Paracetamol": 104, "IronTablets": 46, "IVFluids": 22, "Artemisinin": 11},
    "PHC_TH_001": {"ORS": 164, "Paracetamol": 142, "IronTablets": 58, "IVFluids": 31, "Artemisinin": 16},
    "PHC_TH_002": {"ORS": 148, "Paracetamol": 124, "IronTablets": 51, "IVFluids": 27, "Artemisinin": 13},
    "PHC_PU_001": {"ORS": 168, "Paracetamol": 142, "IronTablets": 48, "IVFluids": 22, "Artemisinin": 9},
    "PHC_PU_002": {"ORS": 1620, "Paracetamol": 98, "IronTablets": 30, "IVFluids": 10, "Artemisinin": 5},  # ORS anomaly
    "PHC_PU_003": {"ORS": 132, "Paracetamol": 110, "IronTablets": 36, "IVFluids": 16, "Artemisinin": 7},
    "PHC_CT_001": {"ORS": 154, "Paracetamol": 140, "IronTablets": 58, "IVFluids": 30, "Artemisinin": 12},
    "PHC_CT_002": {"ORS": 102, "Paracetamol": 88, "IronTablets": 36, "IVFluids": 18, "Artemisinin": 8},
    "PHC_KH_001": {"ORS": 176, "Paracetamol": 160, "IronTablets": 64, "IVFluids": 28, "Artemisinin": 11},
    "PHC_KH_002": {"ORS": 124, "Paracetamol": 108, "IronTablets": 44, "IVFluids": 20, "Artemisinin": 8},
    "PHC_BL_001": {"ORS": 170, "Paracetamol": 148, "IronTablets": 56, "IVFluids": 26, "Artemisinin": 10},
    "PHC_BL_002": {"ORS": 118, "Paracetamol": 96, "IronTablets": 38, "IVFluids": 16, "Artemisinin": 6},
    "PHC_BM_001": {"ORS": 148, "Paracetamol": 118, "IronTablets": 42, "IVFluids": 18, "Artemisinin": 8},
    "PHC_BM_002": {"ORS": 132, "Paracetamol": 102, "IronTablets": 36, "IVFluids": 16, "Artemisinin": 7},
    "PHC_BM_003": {"ORS": 110, "Paracetamol": 88, "IronTablets": 28, "IVFluids": 12, "Artemisinin": 420},  # Artemisinin anomaly
    "PHC_JD_001": {"ORS": 150, "Paracetamol": 132, "IronTablets": 54, "IVFluids": 26, "Artemisinin": 14},
    "PHC_JD_002": {"ORS": 98, "Paracetamol": 86, "IronTablets": 34, "IVFluids": 16, "Artemisinin": 9},
    "PHC_JP_001": {"ORS": 188, "Paracetamol": 210, "IronTablets": 78, "IVFluids": 32, "Artemisinin": 16},
    "PHC_JP_002": {"ORS": 142, "Paracetamol": 128, "IronTablets": 52, "IVFluids": 24, "Artemisinin": 12},
    "PHC_UD_001": {"ORS": 154, "Paracetamol": 136, "IronTablets": 48, "IVFluids": 22, "Artemisinin": 11},
    "PHC_UD_002": {"ORS": 116, "Paracetamol": 100, "IronTablets": 40, "IVFluids": 18, "Artemisinin": 8},
}

WEEK_DAYS = 7


def detect_leakage(weeks: int = 4) -> list:
    results = []
    for phc in MOCK_PHCS:
        phc_id = phc["id"]
        footfall = phc["avg_daily_footfall"] * WEEK_DAYS * weeks
        dispensed = REPORTED_DISPENSED.get(phc_id, {})
        flags = []

        for medicine, avg_per_patient in AVG_CONSUMPTION_PER_PATIENT.items():
            expected = footfall * avg_per_patient
            actual = dispensed.get(medicine, 0)
            if expected == 0:
                continue
            ratio = actual / expected
            if ratio > 2.5:
                severity = "HIGH" if ratio > 4.0 else "MEDIUM"
                flags.append({
                    "medicine": medicine,
                    "reported_dispensed": actual,
                    "expected_consumption": round(expected, 0),
                    "anomaly_ratio": round(ratio, 2),
                    "severity": severity,
                })

        anomaly_score = min(100, int(sum(f["anomaly_ratio"] for f in flags) * 10)) if flags else 0

        results.append({
            "phc_id": phc_id,
            "phc_name": phc["name"],
            "district": phc["district"],
            "block": phc["block"],
            "footfall_period": footfall,
            "anomaly_score": anomaly_score,
            "flags": flags,
            "status": "FLAGGED" if flags else "NORMAL",
            "weeks_analysed": weeks,
        })

    return sorted(results, key=lambda x: x["anomaly_score"], reverse=True)
