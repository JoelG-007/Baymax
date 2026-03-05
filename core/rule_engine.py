def check_emergency(record):
    red_flags = [
        "chest pain", "difficulty breathing", "unconscious",
        "heart attack", "stroke", "seizure", "not breathing",
        "severe bleeding", "choking", "overdose", "suicidal",
        "loss of consciousness", "severe chest tightness",
        "sudden weakness", "sudden numbness", "sudden confusion",
        "sudden trouble speaking", "sudden vision loss",
        "sudden severe headache", "sudden dizziness", "sudden loss of balance",
        "severe abdominal pain", "severe allergic reaction",
        "severe burn", "severe trauma", "severe bleeding that won't stop",
        "severe head injury", "severe eye injury", "severe neck or back pain",
        "severe difficulty breathing", "severe chest pain that radiates",
        "severe weakness or numbness", "severe confusion or disorientation",
        "severe vomiting or diarrhea", "severe dehydration", "severe allergic reaction with swelling",
        "severe burn with charred skin", "severe trauma with heavy bleeding",
        "severe head injury with loss of consciousness", "severe eye injury with vision loss",
        "severe neck or back pain with loss of sensation",
        "severe difficulty breathing with bluish lips or face", 
        "severe chest pain that radiates to arm or jaw", "severe weakness or numbness on one side of body",
        "severe confusion or disorientation with inability to recognize loved ones",
    ]
    symptom_lower = record["symptom"].lower()
    return any(flag in symptom_lower for flag in red_flags)