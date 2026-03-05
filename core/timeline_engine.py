from database.crud import get_health_events, get_document_summaries

def get_combined_timeline(user_id):
    symptoms = get_health_events(user_id)
    documents = get_document_summaries(user_id)

    combined = []

    for s in symptoms:
        combined.append({
            "type": "Symptom",
            "description": s.symptom,
            "timestamp": s.timestamp
        })

    for d in documents:
        combined.append({
            "type": "Document",
            "description": d.extracted_summary,
            "timestamp": d.created_at
        })

    combined.sort(key=lambda x: x["timestamp"])
    return combined