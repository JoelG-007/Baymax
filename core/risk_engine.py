import numpy as np
import json
from database.crud import get_active_health_events, get_document_summaries


def calculate_risk_score(user_id):
    events = get_active_health_events(user_id)   # only active, unresolved symptoms
    documents = get_document_summaries(user_id)

    severity_map = {
        "Mild": 1,
        "Moderate": 2,
        "Severe": 3
    }

    # --------------------------
    # 1. Symptom Severity Score
    # --------------------------
    if events:
        severity_scores = [severity_map.get(e.severity, 1) for e in events]

        avg_severity = np.mean(severity_scores)
        recent = severity_scores[-3:] if len(severity_scores) >= 3 else severity_scores
        recent_avg = np.mean(recent)

        symptom_score = (avg_severity * 15) + (recent_avg * 20)
    else:
        symptom_score = 0

    # --------------------------
    # 2. Lab Parameter Score
    # --------------------------
    lab_score = 0

    for d in documents:
        if not d.key_parameters_json:
            continue

        params = json.loads(d.key_parameters_json)

        for key, value in params.items():

            if key == "HbA1c":
                if value > 6.5:
                    lab_score += 20
                elif value > 5.7:
                    lab_score += 10

            if key == "Cholesterol":
                if value > 240:
                    lab_score += 20
                elif value > 200:
                    lab_score += 10

            if key == "Blood Sugar":
                if value > 200:
                    lab_score += 20
                elif value > 140:
                    lab_score += 10

    # --------------------------
    # 3. Final Composite Score
    # --------------------------
    risk_score = min(100, round(symptom_score + lab_score))

    # --------------------------
    # 4. Categorization
    # --------------------------
    if risk_score < 25:
        level = "Low"
    elif risk_score < 50:
        level = "Moderate"
    elif risk_score < 75:
        level = "High"
    else:
        level = "Critical"

    return risk_score, level