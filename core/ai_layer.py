import os
from dotenv import load_dotenv
from groq import Groq
import re 
import json

from database.crud import get_active_health_events, get_document_summaries
from core.risk_engine import calculate_risk_score

# -----------------------------------
# Load Environment Variables
# -----------------------------------
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Ensure .env exists in project root."
    )

client = Groq(api_key=api_key)

MODEL_NAME = "llama-3.1-8b-instant"


# ===================================
# Chat Advisory Generator
# ===================================
def generate_advisory(record, user_id, chat_history=None):

    history_context = ""
    if chat_history:
        recent_messages = chat_history[-4:]
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]
            history_context += f"{role.upper()}: {content}\n"

    prompt = f"""
    You are Baymax, a calm and professional health intelligence assistant.

    Conversation History:
    {history_context}

    Current Symptom:
    Symptom: {record['symptom']}
    Severity: {record['severity']}
    Body Region: {record['body_region']}

    Provide:
    1. Brief explanation
    2. Possible causes (general)
    3. Practical steps
    4. When to seek medical care
    5. If you are unsure, say so clearly do not make up information.

    Keep response under 150 words.
    Do NOT diagnose.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.9,
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception:
        return (
            "⚠ AI service unavailable.\n\n"
            "Please check API configuration."
        )

# ===================================
# Contextual Reply Generator
# ===================================
def generate_contextual_reply(user_input, user_id, chat_history=None):
    """
    Handles follow-up questions and document-based queries.
    Uses chat history + stored document summaries as context.
    Does NOT extract symptoms. Does NOT write to the database.
    """

    history_context = ""
    if chat_history:
        for msg in chat_history[-6:]:
            history_context += f"{msg['role'].upper()}: {msg['content']}\n"

    docs = get_document_summaries(user_id)
    doc_context = ""
    if docs:
        for d in docs:
            if d.extracted_summary:
                doc_context += f"- Report Type: {d.report_type or 'Unknown'}\n"
                doc_context += f"  Summary: {d.extracted_summary}\n"
                if d.severity_flag:
                    doc_context += f"  Risk Flag: {d.severity_flag}\n"
                doc_context += "\n"

    if not doc_context:
        doc_context = "No medical documents have been uploaded yet."

    prompt = f"""
    You are Baymax, a calm and professional health intelligence assistant.

    The user is asking a follow-up question or a question about their medical documents.
    This is NOT a new symptom report. Do NOT treat it as one.

    Conversation History:
    {history_context}

    Uploaded Medical Document Summaries:
    {doc_context}

    User Question: {user_input}

    Guidelines:
    - Answer based only on the available context above.
    - If the answer is in the documents, reference the relevant finding.
    - Do NOT diagnose. Do NOT invent information.
    - If you cannot answer from available context, say so clearly.

    Keep response under 200 words.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.9,
            max_tokens=400
        )
        return response.choices[0].message.content

    except Exception:
        return (
            "⚠ AI service unavailable.\n\n"
            "Please check API configuration."
        )

# ===================================
# Risk Explanation Generator
# ===================================
def explain_risk_score(user_id):

    risk_score, risk_level = calculate_risk_score(user_id)

    events = get_active_health_events(user_id)
    documents = get_document_summaries(user_id)

    history_text = "\n".join(
        [f"{e.symptom} ({e.severity})" for e in events[-5:]]
    )

    doc_flags = [
        d.severity_flag for d in documents if d.severity_flag == "High"
    ]

    prompt = f"""
    User Health Risk Score: {risk_score}/100
    Risk Level: {risk_level}

    Recent Symptoms:
    {history_text}

    High Risk Documents: {len(doc_flags)}

    Explain clearly:
    - Why the score is at this level
    - What contributed most
    - General precautions to consider

    Do NOT provide diagnosis.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.9,
            max_tokens=400
        )

        return response.choices[0].message.content

    except Exception:
        return (
            "⚠ Unable to generate AI explanation.\n\n"
            "Check API configuration."
        )

def classify_intent(text):
    prompt = f"""
    Classify the user's message into ONE of these categories:

    - greeting       : casual hello, introduction, or small talk
    - symptom        : user is reporting a NEW or WORSENING physical symptom they are currently experiencing
    - document_query : user is asking a question about their uploaded medical report, lab results, or health documents
    - followup       : user is continuing a conversation about a symptom already mentioned, or asking what to do next
    - unclear        : cannot determine intent from the message

    Message: "{text}"

    Rules:
    - Choose ONLY one category.
    - Messages starting with "and" or "also" that mention a symptom are ALWAYS symptom.
    - If the user mentions a symptom AND asks about their report, choose document_query.
    - If the user says things like "what about my headache", "should I be worried", choose followup.
    - Short phrases like "how are you", "hello", "hi" are greeting ONLY if no symptom is mentioned.
    - Respond with only one word, exactly as listed above.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=15
        )
        return response.choices[0].message.content.strip().lower()
    except Exception:
        return "unclear"

def extract_parameters_from_report(text):
    """
    Uses the LLM to extract structured data from any medical report text.
    Returns a dict with report_type, summary, parameters, and doctor_name.
    """

    prompt = f"""
    You are a medical data extraction assistant.

    Extract structured information from the following medical report text.

    Return ONLY a valid JSON object with this exact structure:
    {{
        "report_type": "string (e.g. Blood Test, Urine Test, Thyroid Panel, CBC, etc.)",
        "summary": "string (1-2 sentence summary of key findings)",
        "doctor_name": "string or null",
        "parameters": {{
            "parameter_name": numeric_value,
            ...
        }}
    }}

    Rules:
    - Extract ALL numeric lab parameters you can find (e.g. HbA1c, WBC, RBC, TSH, ALT, Creatinine, Haemoglobin, Platelets, etc.)
    - Parameter names should be clean and readable (e.g. "Haemoglobin" not "HGB")
    - Values must be numbers only — no units, no strings
    - If a value is a range like "4.5-5.5", extract the actual result value only
    - If you cannot find a value, do not include that parameter
    - Do not include reference ranges as parameter values
    - Return ONLY the JSON object, no explanation, no markdown, no code fences

    Medical Report Text:
    {text[:3000]}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=800
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model wraps in ```json
        raw = re.sub(r"```json|```", "", raw).strip()

        import json
        result = json.loads(raw)

        # Ensure parameters values are all numeric
        clean_params = {}
        for k, v in result.get("parameters", {}).items():
            try:
                clean_params[k] = float(v)
            except (ValueError, TypeError):
                pass

        result["parameters"] = clean_params
        return result

    except Exception:
        return {
            "report_type": "Lab Report",
            "summary": text[:400],
            "doctor_name": None,
            "parameters": {}
        }