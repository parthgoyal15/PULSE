MOCK_PHCS = [
    # Raigad District (HIGH RISK — coastal, dengue prone)
    {"id": "PHC_RG_001", "name": "PHC Mahad", "district": "Raigad", "state": "Maharashtra",
     "lat": 18.0849, "lng": 73.4162, "block": "Mahad",
     "stock": {"ORS": 120, "Paracetamol": 89, "IronTablets": 12, "IVFluids": 45, "Artemisinin": 30},
     "beds": {"total": 12, "occupied": 9}, "staff": {"total": 8, "present": 6},
     "avg_daily_footfall": 42},
    {"id": "PHC_RG_002", "name": "PHC Poladpur", "district": "Raigad", "state": "Maharashtra",
     "lat": 17.9712, "lng": 73.3598, "block": "Poladpur",
     "stock": {"ORS": 80, "Paracetamol": 145, "IronTablets": 8, "IVFluids": 20, "Artemisinin": 15},
     "beds": {"total": 10, "occupied": 8}, "staff": {"total": 7, "present": 5},
     "avg_daily_footfall": 38},
    {"id": "PHC_RG_003", "name": "PHC Alibag", "district": "Raigad", "state": "Maharashtra",
     "lat": 18.6414, "lng": 72.8722, "block": "Alibag",
     "stock": {"ORS": 320, "Paracetamol": 210, "IronTablets": 95, "IVFluids": 110, "Artemisinin": 60},
     "beds": {"total": 15, "occupied": 7}, "staff": {"total": 10, "present": 9},
     "avg_daily_footfall": 55},
    {"id": "PHC_RG_004", "name": "PHC Pen", "district": "Raigad", "state": "Maharashtra",
     "lat": 18.7378, "lng": 73.0933, "block": "Pen",
     "stock": {"ORS": 165, "Paracetamol": 78, "IronTablets": 22, "IVFluids": 55, "Artemisinin": 40},
     "beds": {"total": 10, "occupied": 7}, "staff": {"total": 8, "present": 7},
     "avg_daily_footfall": 35},

    # Pune District (MEDIUM RISK)
    {"id": "PHC_PN_001", "name": "PHC Hadapsar", "district": "Pune", "state": "Maharashtra",
     "lat": 18.5018, "lng": 73.9260, "block": "Haveli",
     "stock": {"ORS": 280, "Paracetamol": 320, "IronTablets": 140, "IVFluids": 90, "Artemisinin": 50},
     "beds": {"total": 20, "occupied": 12}, "staff": {"total": 14, "present": 11},
     "avg_daily_footfall": 88},
    {"id": "PHC_PN_002", "name": "PHC Khed", "district": "Pune", "state": "Maharashtra",
     "lat": 18.8510, "lng": 73.9970, "block": "Khed",
     "stock": {"ORS": 190, "Paracetamol": 240, "IronTablets": 110, "IVFluids": 65, "Artemisinin": 35},
     "beds": {"total": 12, "occupied": 6}, "staff": {"total": 9, "present": 8},
     "avg_daily_footfall": 52},
    {"id": "PHC_PN_003", "name": "PHC Baramati", "district": "Pune", "state": "Maharashtra",
     "lat": 18.1522, "lng": 74.5794, "block": "Baramati",
     "stock": {"ORS": 410, "Paracetamol": 380, "IronTablets": 190, "IVFluids": 140, "Artemisinin": 75},
     "beds": {"total": 18, "occupied": 9}, "staff": {"total": 12, "present": 12},
     "avg_daily_footfall": 70},

    # Nashik District (LOW RISK — surplus district)
    {"id": "PHC_NK_001", "name": "PHC Igatpuri", "district": "Nashik", "state": "Maharashtra",
     "lat": 19.6957, "lng": 73.5607, "block": "Igatpuri",
     "stock": {"ORS": 580, "Paracetamol": 490, "IronTablets": 280, "IVFluids": 200, "Artemisinin": 120},
     "beds": {"total": 14, "occupied": 5}, "staff": {"total": 10, "present": 10},
     "avg_daily_footfall": 40},
    {"id": "PHC_NK_002", "name": "PHC Trimbak", "district": "Nashik", "state": "Maharashtra",
     "lat": 19.9352, "lng": 73.5314, "block": "Trimbakeshwar",
     "stock": {"ORS": 620, "Paracetamol": 540, "IronTablets": 310, "IVFluids": 185, "Artemisinin": 95},
     "beds": {"total": 10, "occupied": 3}, "staff": {"total": 8, "present": 8},
     "avg_daily_footfall": 30},
    {"id": "PHC_NK_003", "name": "PHC Sinnar", "district": "Nashik", "state": "Maharashtra",
     "lat": 19.8481, "lng": 74.0022, "block": "Sinnar",
     "stock": {"ORS": 450, "Paracetamol": 410, "IronTablets": 220, "IVFluids": 160, "Artemisinin": 80},
     "beds": {"total": 12, "occupied": 4}, "staff": {"total": 9, "present": 9},
     "avg_daily_footfall": 36},

    # Thane District (MEDIUM RISK)
    {"id": "PHC_TH_001", "name": "PHC Shahapur", "district": "Thane", "state": "Maharashtra",
     "lat": 19.4597, "lng": 73.3264, "block": "Shahapur",
     "stock": {"ORS": 210, "Paracetamol": 180, "IronTablets": 75, "IVFluids": 70, "Artemisinin": 45},
     "beds": {"total": 12, "occupied": 8}, "staff": {"total": 9, "present": 7},
     "avg_daily_footfall": 48},
    {"id": "PHC_TH_002", "name": "PHC Murbad", "district": "Thane", "state": "Maharashtra",
     "lat": 19.2564, "lng": 73.3941, "block": "Murbad",
     "stock": {"ORS": 155, "Paracetamol": 130, "IronTablets": 55, "IVFluids": 40, "Artemisinin": 25},
     "beds": {"total": 10, "occupied": 7}, "staff": {"total": 8, "present": 6},
     "avg_daily_footfall": 44},

    # Odisha — Puri (CRITICAL flood / diarrhea corridor)
    {"id": "PHC_PU_001", "name": "PHC Puri Sadar", "district": "Puri", "state": "Odisha",
     "lat": 19.8135, "lng": 85.8312, "block": "Puri Sadar",
     "stock": {"ORS": 55, "Paracetamol": 70, "IronTablets": 40, "IVFluids": 18, "Artemisinin": 12},
     "beds": {"total": 14, "occupied": 12}, "staff": {"total": 9, "present": 6},
     "avg_daily_footfall": 62},
    {"id": "PHC_PU_002", "name": "PHC Konark", "district": "Puri", "state": "Odisha",
     "lat": 19.8876, "lng": 86.0945, "block": "Gop",
     "stock": {"ORS": 40, "Paracetamol": 95, "IronTablets": 28, "IVFluids": 12, "Artemisinin": 8},
     "beds": {"total": 10, "occupied": 9}, "staff": {"total": 7, "present": 5},
     "avg_daily_footfall": 48},
    {"id": "PHC_PU_003", "name": "PHC Satyabadi", "district": "Puri", "state": "Odisha",
     "lat": 19.9502, "lng": 85.6784, "block": "Satyabadi",
     "stock": {"ORS": 72, "Paracetamol": 110, "IronTablets": 36, "IVFluids": 22, "Artemisinin": 10},
     "beds": {"total": 12, "occupied": 8}, "staff": {"total": 8, "present": 6},
     "avg_daily_footfall": 44},

    # Odisha — Cuttack (LOW RISK surplus)
    {"id": "PHC_CT_001", "name": "PHC Cuttack Sadar", "district": "Cuttack", "state": "Odisha",
     "lat": 20.4625, "lng": 85.8830, "block": "Cuttack Sadar",
     "stock": {"ORS": 640, "Paracetamol": 520, "IronTablets": 260, "IVFluids": 210, "Artemisinin": 90},
     "beds": {"total": 18, "occupied": 6}, "staff": {"total": 12, "present": 11},
     "avg_daily_footfall": 50},
    {"id": "PHC_CT_002", "name": "PHC Athagarh", "district": "Cuttack", "state": "Odisha",
     "lat": 20.5118, "lng": 85.6290, "block": "Athagarh",
     "stock": {"ORS": 510, "Paracetamol": 430, "IronTablets": 200, "IVFluids": 175, "Artemisinin": 70},
     "beds": {"total": 12, "occupied": 4}, "staff": {"total": 8, "present": 8},
     "avg_daily_footfall": 34},

    # Odisha — Khordha (MEDIUM)
    {"id": "PHC_KH_001", "name": "PHC Jatni", "district": "Khordha", "state": "Odisha",
     "lat": 20.1597, "lng": 85.7074, "block": "Jatni",
     "stock": {"ORS": 240, "Paracetamol": 210, "IronTablets": 95, "IVFluids": 80, "Artemisinin": 40},
     "beds": {"total": 14, "occupied": 7}, "staff": {"total": 10, "present": 9},
     "avg_daily_footfall": 58},
    {"id": "PHC_KH_002", "name": "PHC Balianta", "district": "Khordha", "state": "Odisha",
     "lat": 20.2961, "lng": 85.9010, "block": "Balianta",
     "stock": {"ORS": 190, "Paracetamol": 175, "IronTablets": 80, "IVFluids": 60, "Artemisinin": 32},
     "beds": {"total": 10, "occupied": 5}, "staff": {"total": 8, "present": 7},
     "avg_daily_footfall": 41},

    # Odisha — Balasore (HIGH flood corridor)
    {"id": "PHC_BL_001", "name": "PHC Balasore Sadar", "district": "Balasore", "state": "Odisha",
     "lat": 21.4934, "lng": 86.9335, "block": "Balasore Sadar",
     "stock": {"ORS": 130, "Paracetamol": 150, "IronTablets": 60, "IVFluids": 48, "Artemisinin": 22},
     "beds": {"total": 16, "occupied": 11}, "staff": {"total": 11, "present": 8},
     "avg_daily_footfall": 56},
    {"id": "PHC_BL_002", "name": "PHC Remuna", "district": "Balasore", "state": "Odisha",
     "lat": 21.5290, "lng": 86.8710, "block": "Remuna",
     "stock": {"ORS": 95, "Paracetamol": 120, "IronTablets": 44, "IVFluids": 30, "Artemisinin": 16},
     "beds": {"total": 10, "occupied": 7}, "staff": {"total": 7, "present": 5},
     "avg_daily_footfall": 39},

    # Rajasthan — Barmer (CRITICAL malaria / heat corridor)
    {"id": "PHC_BM_001", "name": "PHC Barmer Sadar", "district": "Barmer", "state": "Rajasthan",
     "lat": 25.7521, "lng": 71.3960, "block": "Barmer",
     "stock": {"ORS": 48, "Paracetamol": 90, "IronTablets": 35, "IVFluids": 16, "Artemisinin": 8},
     "beds": {"total": 12, "occupied": 10}, "staff": {"total": 8, "present": 5},
     "avg_daily_footfall": 51},
    {"id": "PHC_BM_002", "name": "PHC Balotra", "district": "Barmer", "state": "Rajasthan",
     "lat": 25.8300, "lng": 72.2400, "block": "Balotra",
     "stock": {"ORS": 62, "Paracetamol": 110, "IronTablets": 40, "IVFluids": 20, "Artemisinin": 10},
     "beds": {"total": 10, "occupied": 8}, "staff": {"total": 7, "present": 5},
     "avg_daily_footfall": 44},
    {"id": "PHC_BM_003", "name": "PHC Siwana", "district": "Barmer", "state": "Rajasthan",
     "lat": 25.6510, "lng": 72.5910, "block": "Siwana",
     "stock": {"ORS": 38, "Paracetamol": 75, "IronTablets": 22, "IVFluids": 12, "Artemisinin": 6},
     "beds": {"total": 8, "occupied": 7}, "staff": {"total": 6, "present": 4},
     "avg_daily_footfall": 36},

    # Rajasthan — Jodhpur (LOW RISK surplus)
    {"id": "PHC_JD_001", "name": "PHC Jodhpur Rural", "district": "Jodhpur", "state": "Rajasthan",
     "lat": 26.2389, "lng": 73.0243, "block": "Jodhpur",
     "stock": {"ORS": 580, "Paracetamol": 490, "IronTablets": 240, "IVFluids": 190, "Artemisinin": 140},
     "beds": {"total": 16, "occupied": 6}, "staff": {"total": 11, "present": 10},
     "avg_daily_footfall": 48},
    {"id": "PHC_JD_002", "name": "PHC Osian", "district": "Jodhpur", "state": "Rajasthan",
     "lat": 26.7240, "lng": 72.8960, "block": "Osian",
     "stock": {"ORS": 460, "Paracetamol": 410, "IronTablets": 200, "IVFluids": 155, "Artemisinin": 110},
     "beds": {"total": 12, "occupied": 4}, "staff": {"total": 8, "present": 8},
     "avg_daily_footfall": 32},

    # Rajasthan — Jaipur (MEDIUM)
    {"id": "PHC_JP_001", "name": "PHC Amber", "district": "Jaipur", "state": "Rajasthan",
     "lat": 26.9855, "lng": 75.8513, "block": "Amber",
     "stock": {"ORS": 260, "Paracetamol": 240, "IronTablets": 120, "IVFluids": 85, "Artemisinin": 45},
     "beds": {"total": 18, "occupied": 9}, "staff": {"total": 12, "present": 10},
     "avg_daily_footfall": 72},
    {"id": "PHC_JP_002", "name": "PHC Chomu", "district": "Jaipur", "state": "Rajasthan",
     "lat": 27.1680, "lng": 75.7230, "block": "Chomu",
     "stock": {"ORS": 210, "Paracetamol": 195, "IronTablets": 95, "IVFluids": 70, "Artemisinin": 38},
     "beds": {"total": 12, "occupied": 6}, "staff": {"total": 9, "present": 8},
     "avg_daily_footfall": 54},

    # Rajasthan — Udaipur (MEDIUM–HIGH malaria watch)
    {"id": "PHC_UD_001", "name": "PHC Girwa", "district": "Udaipur", "state": "Rajasthan",
     "lat": 24.5854, "lng": 73.7125, "block": "Girwa",
     "stock": {"ORS": 175, "Paracetamol": 160, "IronTablets": 70, "IVFluids": 55, "Artemisinin": 28},
     "beds": {"total": 14, "occupied": 8}, "staff": {"total": 10, "present": 8},
     "avg_daily_footfall": 50},
    {"id": "PHC_UD_002", "name": "PHC Salumber", "district": "Udaipur", "state": "Rajasthan",
     "lat": 24.1350, "lng": 74.0440, "block": "Salumber",
     "stock": {"ORS": 140, "Paracetamol": 130, "IronTablets": 58, "IVFluids": 42, "Artemisinin": 22},
     "beds": {"total": 10, "occupied": 6}, "staff": {"total": 7, "present": 6},
     "avg_daily_footfall": 38},
]

DISTRICTS = {
    "Raigad":   {"lat": 18.3164, "lng": 73.1812, "state": "Maharashtra", "phc_count": 41, "population": 2635394},
    "Pune":     {"lat": 18.5204, "lng": 73.8567, "state": "Maharashtra", "phc_count": 87, "population": 9429408},
    "Nashik":   {"lat": 19.9975, "lng": 73.7898, "state": "Maharashtra", "phc_count": 62, "population": 6109052},
    "Thane":    {"lat": 19.2183, "lng": 72.9781, "state": "Maharashtra", "phc_count": 53, "population": 11060148},
    "Puri":     {"lat": 19.8135, "lng": 85.8312, "state": "Odisha", "phc_count": 38, "population": 1698730},
    "Cuttack":  {"lat": 20.4625, "lng": 85.8830, "state": "Odisha", "phc_count": 52, "population": 2624470},
    "Khordha":  {"lat": 20.1820, "lng": 85.6180, "state": "Odisha", "phc_count": 34, "population": 2251673},
    "Balasore": {"lat": 21.4934, "lng": 86.9335, "state": "Odisha", "phc_count": 47, "population": 2320529},
    "Barmer":   {"lat": 25.7521, "lng": 71.3960, "state": "Rajasthan", "phc_count": 61, "population": 2603751},
    "Jodhpur":  {"lat": 26.2389, "lng": 73.0243, "state": "Rajasthan", "phc_count": 74, "population": 3687165},
    "Jaipur":   {"lat": 26.9124, "lng": 75.7873, "state": "Rajasthan", "phc_count": 92, "population": 6626178},
    "Udaipur":  {"lat": 24.5854, "lng": 73.7125, "state": "Rajasthan", "phc_count": 58, "population": 3068420},
}

OPERATIONAL_STATES = ["Maharashtra", "Odisha", "Rajasthan"]

OUTBREAK_SCENARIO = {
    "Maharashtra": {"district": "Raigad", "kind": "dengue"},
    "Odisha": {"district": "Puri", "kind": "flood"},
    "Rajasthan": {"district": "Barmer", "kind": "malaria"},
}

STATE_META = {
    "Maharashtra": {
        "lat": 19.2, "lng": 73.8, "zoom": 7,
        "language": "mr", "language_name": "Marathi", "geo_code": "IN-MH",
    },
    "Odisha": {
        "lat": 20.5, "lng": 85.5, "zoom": 7,
        "language": "or", "language_name": "Odia", "geo_code": "IN-OR",
    },
    "Rajasthan": {
        "lat": 26.4, "lng": 73.8, "zoom": 6.5,
        "language": "hi", "language_name": "Hindi", "geo_code": "IN-RJ",
    },
}


def districts_in_state(state: str) -> list[str]:
    return [name for name, info in DISTRICTS.items() if info["state"] == state]


def state_for_district(district: str) -> str:
    return DISTRICTS.get(district, {}).get("state", "Maharashtra")


# National state-level mock data
NATIONAL_STATES = [
    {"name": "Maharashtra",    "lat": 19.7515, "lng": 75.7139, "risk_score": 72, "risk_level": "HIGH",     "phc_count": 1816, "population": 112374333, "primary_driver": "Dengue surge + early monsoon, coastal districts critical"},
    {"name": "Odisha",         "lat": 20.9517, "lng": 85.0985, "risk_score": 84, "risk_level": "CRITICAL", "phc_count": 1505, "population": 41974218,  "primary_driver": "Post-flood diarrheal surge, 6 districts affected"},
    {"name": "Uttar Pradesh",  "lat": 26.8467, "lng": 80.9462, "risk_score": 61, "risk_level": "HIGH",     "phc_count": 3497, "population": 199812341, "primary_driver": "Encephalitis season onset, low ORS stocks in eastern districts"},
    {"name": "Karnataka",      "lat": 15.3173, "lng": 75.7139, "risk_score": 44, "risk_level": "MEDIUM",   "phc_count": 2353, "population": 61095297,  "primary_driver": "Moderate dengue signals, stock levels adequate"},
    {"name": "Tamil Nadu",     "lat": 11.1271, "lng": 78.6569, "risk_score": 28, "risk_level": "LOW",      "phc_count": 1614, "population": 72147030,  "primary_driver": "All signals within normal range"},
    {"name": "Rajasthan",      "lat": 27.0238, "lng": 74.2179, "risk_score": 38, "risk_level": "MEDIUM",   "phc_count": 2068, "population": 68548437,  "primary_driver": "Desert malaria watch in Barmer belt; heat-related ORS demand"},
    {"name": "West Bengal",    "lat": 22.9868, "lng": 87.8550, "risk_score": 55, "risk_level": "HIGH",     "phc_count": 909,  "population": 91276115,  "primary_driver": "Monsoon flooding + cholera risk in delta districts"},
    {"name": "Madhya Pradesh", "lat": 22.9734, "lng": 78.6569, "risk_score": 32, "risk_level": "LOW",      "phc_count": 1172, "population": 72626809,  "primary_driver": "Stable — surplus stock available for redistribution"},
    {"name": "Bihar",          "lat": 25.0961, "lng": 85.3131, "risk_score": 67, "risk_level": "HIGH",     "phc_count": 1886, "population": 104099452, "primary_driver": "Flood corridor active, Kosi belt PHCs at risk"},
    {"name": "Kerala",         "lat": 10.8505, "lng": 76.2711, "risk_score": 21, "risk_level": "LOW",      "phc_count": 931,  "population": 33406061,  "primary_driver": "Best-performing state model, strong supply chain"},
    {"name": "Gujarat",        "lat": 22.2587, "lng": 71.1924, "risk_score": 35, "risk_level": "MEDIUM",   "phc_count": 1187, "population": 60439692,  "primary_driver": "Seasonal malaria watch, Saurashtra under monitor"},
    {"name": "Andhra Pradesh", "lat": 15.9129, "lng": 79.7400, "risk_score": 48, "risk_level": "MEDIUM",   "phc_count": 1144, "population": 49386799,  "primary_driver": "Dengue corridor from Karnataka crossing border"},
]
