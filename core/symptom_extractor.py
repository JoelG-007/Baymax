import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# -----------------------
# Symptom Terms
# -----------------------
SYMPTOM_TERMS = [

    # General / Systemic
    "pain", "ache", "fever", "chills", "shiver", "sweat",
    "fatigue", "tired", "weak", "lethargy", "malaise",
    "faint", "dizzy", "vertigo", "confusion", "disorientation",
    "weight loss", "weight gain", "appetite", "thirst",
    "insomnia", "sleepy", "night sweats", "sweat", "swelling", 
    "inflammation", "lump", "bump", "mass", "nodule", "ulcer", "sore",
    "bleed", "bruise", "rash", "itch", "redness", "discharge",
    "pain", "ache", "soreness", "tenderness", "stiffness",
    "nausea", "vomit", "diarrhea", "constipation", "indigestion", 
    "cramp", "bloating", "gas", "heartburn", "acid reflux",

    # Respiratory & Cardiac
    "cough", "phlegm", "mucus", "congestion", "runny nose",
    "sneeze", "wheeze", "shortness of breath", "dyspnea",
    "gasping", "chest pain", "tightness", "palpitations",
    "rapid heart", "snoring", "breathing","cold", "flu", 
    "covid", "coronavirus", ""

    # Digestive (GI)
    "nausea", "vomit", "diarrhea", "constipation",
    "bloating", "gas", "heartburn", "acid reflux",
    "indigestion", "stomach ache", "cramp",
    "swallowing", "dehydration",

    # Neurological & Sensory
    "headache", "migraine", "numbness", "tingling",
    "pins and needles", "seizure", "tremor", "spasm",
    "paralysis", "blurry vision", "double vision",
    "tinnitus", "ringing in ears",
    "loss of taste", "loss of smell",

    # Skin & Musculoskeletal
    "rash", "itch", "redness", "swelling",
    "inflammation", "stiffness", "bruise",
    "lesion", "blister", "sore", "burn",
    "joint pain", "muscle ache", "back pain"
]

SEVERITY_WORDS = {
    "mild": "Mild",
    "moderate": "Moderate",
    "severe": "Severe",
    "extreme": "Severe"
}

# -----------------------
# Phrase Matcher
# -----------------------
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(term) for term in SYMPTOM_TERMS]
matcher.add("SYMPTOMS", patterns)


def is_negated(token):
    for child in token.children:
        if child.dep_ == "neg":
            return True
    for ancestor in token.ancestors:
        for child in ancestor.children:
            if child.dep_ == "neg":
                return True
    return False


def extract_symptom(text):
    doc = nlp(text.lower())

    detected_symptoms = []
    detected_severity = "Mild"
    body_region = "General"

    # -----------------------
    # Severity Detection
    # -----------------------
    for token in doc:
        if token.text in SEVERITY_WORDS:
            detected_severity = SEVERITY_WORDS[token.text]

    # -----------------------
    # Multi-word Symptom Detection
    # -----------------------
    matches = matcher(doc)

    for _, start, end in matches:
        span = doc[start:end]

        # Skip negated spans
        if any(is_negated(token) for token in span):
            continue

        detected_symptoms.append(span.text)

    # Remove duplicates
    detected_symptoms = list(set(detected_symptoms))

    # -----------------------
    # Body Region Detection
    # -----------------------
    BODY_PARTS = [
        "head", "chest", "stomach", "back",
        "leg", "arm", "throat", "eye", "ear"
    ]

    for token in doc:
        if token.text in BODY_PARTS:
            body_region = token.text
            break

    # -----------------------
    # Fallback
    # -----------------------
    if not detected_symptoms:
        detected_symptoms.append(text.strip())

    symptom_string = ", ".join(detected_symptoms).strip()

    if not symptom_string:
        symptom_string = "Unspecified discomfort"

    return {
        "symptom": symptom_string,
        "severity": detected_severity,
        "body_region": body_region
    }