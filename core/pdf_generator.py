from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from io import BytesIO
from datetime import datetime
import json

from database.crud import get_health_events, get_document_summaries
from core.risk_engine import calculate_risk_score
from core.ai_layer import explain_risk_score

def generate_pdf_report(user_id, username):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Baymax Health Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"User: {username}", styles["Normal"]))
    elements.append(Paragraph(f"Generated: {datetime.utcnow()}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Risk Score
    risk_score, risk_level = calculate_risk_score(user_id)

    elements.append(Paragraph("<b>Health Risk Summary</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Risk Score: {risk_score}/100", styles["Normal"]))
    elements.append(Paragraph(f"Risk Level: {risk_level}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Symptoms
    events = get_health_events(user_id)

    elements.append(Paragraph("<b>Recent Symptoms</b>", styles["Heading2"]))

    if events:
        symptom_list = []
        for e in events[-5:]:
            symptom_list.append(
                ListItem(Paragraph(f"{e.symptom} ({e.severity})", styles["Normal"]))
            )
        elements.append(ListFlowable(symptom_list))
    else:
        elements.append(Paragraph("No symptoms logged.", styles["Normal"]))

    elements.append(Spacer(1, 0.3 * inch))

    # Lab Parameters
    documents = get_document_summaries(user_id)

    elements.append(Paragraph("<b>Lab Parameters</b>", styles["Heading2"]))

    lab_data = []

    for d in documents:
        if d.key_parameters_json:
            params = json.loads(d.key_parameters_json)
            for key, value in params.items():
                lab_data.append([key, str(value)])

    if lab_data:
        table = Table(lab_data, colWidths=[2 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No lab data available.", styles["Normal"]))

    elements.append(Spacer(1, 0.3 * inch))

    # AI Explanation
    elements.append(Paragraph("<b>AI Risk Explanation</b>", styles["Heading2"]))
    explanation = explain_risk_score(user_id)
    elements.append(Paragraph(explanation, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer

