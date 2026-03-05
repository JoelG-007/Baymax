import re
from core.ai_layer import extract_parameters_from_report


def extract_structured_data(text):
    """
    Uses the LLM to extract structured data from any medical report.
    Falls back to regex for the 3 known parameters if AI fails.
    """
    risk = "Low"

    # --- AI-based extraction ---
    ai_result = extract_parameters_from_report(text)

    parameters = ai_result.get("parameters", {})
    report_type = ai_result.get("report_type", "Lab Report")
    summary = ai_result.get("summary", text[:400])
    doctor_name = ai_result.get("doctor_name") or extract_doctor_name(text)

    # --- Determine risk from extracted parameters ---
    hba1c = parameters.get("HbA1c")
    cholesterol = parameters.get("Cholesterol")
    sugar = parameters.get("Blood Sugar") or parameters.get("Glucose")

    if hba1c and float(hba1c) > 6.5:
        risk = "High"
    if cholesterol and float(cholesterol) > 240:
        risk = "High"
    if sugar and float(sugar) > 200:
        risk = "High"

    # Flag any parameter with "High" or "Abnormal" in the raw text near it
    if re.search(r"\b(high|abnormal|elevated|critical)\b", text, re.IGNORECASE):
        risk = "High"

    return {
        "report_type": report_type,
        "summary": summary,
        "parameters": parameters,
        "risk": risk,
        "doctor_name": doctor_name
    }


def extract_doctor_name(text):
    pattern = r"(Dr\.?\s+[A-Z][a-zA-Z]+\s?[A-Z]?[a-zA-Z]*)"
    matches = re.findall(pattern, text)
    return matches[0] if matches else None