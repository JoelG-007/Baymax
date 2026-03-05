import numpy as np
from database.crud import get_active_health_events


def detect_anomaly(user_id):
    events = get_active_health_events(user_id)

    if len(events) < 4:
        return False, None

    severity_map = {"Mild": 1, "Moderate": 2, "Severe": 3}
    scores = [severity_map.get(e.severity, 1) for e in events]

    baseline = np.mean(scores[:-1])
    latest = scores[-1]

    if latest >= baseline + 1:
        return True, {
            "baseline": round(baseline, 2),
            "latest": latest
        }

    return False, None