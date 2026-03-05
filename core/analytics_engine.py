import pandas as pd
from database.crud import get_active_health_events


def generate_analytics(user_id):
    events = get_active_health_events(user_id)

    if not events:
        return None, None

    data = [{
        "symptom": e.symptom,
        "severity": e.severity,
        "body_region": e.body_region,
        "timestamp": e.timestamp
    } for e in events]

    df = pd.DataFrame(data)

    severity_map = {"Mild": 1, "Moderate": 2, "Severe": 3}

    df["severity_score"] = df["severity"].map(severity_map)
    df = df.sort_values("timestamp")
    df["rolling_avg"] = df["severity_score"].rolling(window=3).mean()

    return df, severity_map