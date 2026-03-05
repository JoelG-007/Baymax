import streamlit as st
from database.crud import get_health_events, get_document_summaries
from core.risk_engine import calculate_risk_score
from core.improvement_engine import detect_improvement
from core.ai_layer import explain_risk_score
from core.pdf_generator import generate_pdf_report
from core.anomaly_engine import detect_anomaly
import plotly.graph_objects as go


def render_dashboard():
    st.title("Health Overview")

    user_id = st.session_state.user["id"]
    username = st.session_state.user["username"]

    symptoms = get_health_events(user_id)
    documents = get_document_summaries(user_id)

    # -----------------------
    # Empty state for new users
    # -----------------------
    if not symptoms and not documents:
        st.info(
            "Welcome to Baymax!, Your personal health-care companion.\n\n" 
            "You have no health data yet.\n\n"
            "- Go to **Health Chat** to log your first symptom\n"
            "- Go to **Documents** to upload a medical report"
        )
        return

    risk_score, risk_level = calculate_risk_score(user_id)
    active_symptoms = [s for s in symptoms if not s.is_resolved]

    # -----------------------
    # Risk Gauge
    # -----------------------
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": "Health Risk Index"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkred" if risk_score > 75 else
                             "orange"  if risk_score > 50 else
                             "yellow"  if risk_score > 25 else
                             "green"},
            "steps": [
                {"range": [0,  25],  "color": "#2ecc71"},
                {"range": [25, 50],  "color": "#f1c40f"},
                {"range": [50, 75],  "color": "#e67e22"},
                {"range": [75, 100], "color": "#e74c3c"},
            ],
        }
    ))

    gauge.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=350)
    st.plotly_chart(gauge, use_container_width=True)

    # -----------------------
    # Metrics
    # -----------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Symptoms", len(active_symptoms))
    col2.metric("Total Logged",     len(symptoms))
    col3.metric("Uploaded Reports", len(documents))
    col4.metric("Risk Score",       f"{risk_score}/100")

    st.markdown("---")

    # -----------------------
    # Action buttons — moved up, side by side
    # -----------------------
    if "pdf_report" not in st.session_state:
        st.session_state.pdf_report = None

    if "risk_explanation" not in st.session_state:
        st.session_state.risk_explanation = None

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Generate Health Report"):
            with st.spinner("Generating report..."):
                st.session_state.pdf_report = generate_pdf_report(user_id, username)

    with col_b:
        if st.button("Explain My Risk"):
            with st.spinner("Analyzing your risk..."):
                st.session_state.risk_explanation = explain_risk_score(user_id)

    if st.session_state.pdf_report:
        st.download_button(
            label="Download Health Report PDF",
            data=st.session_state.pdf_report,
            file_name="baymax_health_report.pdf",
            mime="application/pdf"
        )

    if st.session_state.risk_explanation:
        with st.expander("Why is my risk at this level?"):
            st.write(st.session_state.risk_explanation)

    st.markdown("---")

    # -----------------------
    # Anomaly & Improvement Detection
    # -----------------------
    anomaly_detected, anomaly_details = detect_anomaly(user_id)
    improved, improvement_details = detect_improvement(user_id)

    if anomaly_detected:
        st.error("Sudden increase in symptom severity detected!")
        with st.expander("View anomaly details"):
            st.write(f"Baseline Severity Average: {anomaly_details['baseline']}")
            st.write(f"Latest Severity Score: {anomaly_details['latest']}")
            st.write("Baymax recommends monitoring this closely.")

    if improved:
        st.success("Health trend is improving!")
        with st.expander("View improvement details"):
            st.write(f"Previous Severity Average: {improvement_details['previous_avg']}")
            st.write(f"Recent Severity Average:   {improvement_details['recent_avg']}")
            st.write("Keep maintaining healthy habits.")

    if not anomaly_detected and not improved:
        st.info("No anomalies or sudden changes detected. Your trend looks stable.")

    st.markdown("---")
    st.caption("Baymax continuously evaluates your health trends.")