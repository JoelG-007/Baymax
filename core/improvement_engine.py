import numpy as np
from database.crud import get_active_health_events

def detect_improvement(user_id):
    events = get_active_health_events(user_id)

    if len(events) < 4:
        return False, None

    severity_map = {"Mild": 1, "Moderate": 2, "Severe": 3}
    scores = [severity_map.get(e.severity, 1) for e in events]

    first_half = scores[:len(scores) // 2]
    second_half = scores[len(scores) // 2:]

    first_avg = np.mean(first_half)
    second_avg = np.mean(second_half)

    if second_avg < first_avg - 0.5:
        return True, {
            "previous_avg": round(first_avg, 2),
            "recent_avg": round(second_avg, 2)
        }

    return False, None

