import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.analytics_engine import generate_analytics


def render_analytics():
    st.title("Health Analytics")

    user_id = st.session_state.user["id"]
    df, severity_map = generate_analytics(user_id)

    if df is None or len(df) < 2:
        st.info("Log at least 2 symptoms to see analytics.")
        return

    # -----------------------------
    # Symptom Frequency
    # -----------------------------
    st.subheader("Symptom Frequency")

    freq = df["symptom"].value_counts().reset_index()
    freq.columns = ["Symptom", "Count"]

    fig_freq = px.bar(
        freq,
        x="Symptom",
        y="Count",
        title="Most Frequent Symptoms",
        color="Count",
        color_continuous_scale="Blues"
    )
    fig_freq.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_freq, use_container_width=True)

    # -----------------------------
    # Severity Trend
    # -----------------------------
    st.subheader("Severity Trend Over Time")

    fig_severity = go.Figure()

    fig_severity.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["severity_score"],
        mode="lines+markers",
        name="Severity Score"
    ))

    fig_severity.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["rolling_avg"],
        mode="lines",
        name="Rolling Average (3 logs)",
        line=dict(dash="dash")
    ))

    fig_severity.update_layout(
        yaxis=dict(tickvals=[1, 2, 3], ticktext=["Mild", "Moderate", "Severe"]),
        height=500
    )
    st.plotly_chart(fig_severity, use_container_width=True)

    # -----------------------------
    # Severity Breakdown Pie
    # -----------------------------
    st.subheader("Severity Breakdown")

    sev_counts = df["severity"].value_counts().reset_index()
    sev_counts.columns = ["Severity", "Count"]

    fig_pie = px.pie(
        sev_counts,
        names="Severity",
        values="Count",
        color="Severity",
        color_discrete_map={
            "Mild":     "#2ecc71",
            "Moderate": "#f1c40f",
            "Severe":   "#e74c3c"
        },
        title="Proportion of Symptom Severities"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # -----------------------------
    # Body Region Distribution
    # -----------------------------
    st.subheader("Symptoms by Body Region")

    region_freq = df["body_region"].value_counts().reset_index()
    region_freq.columns = ["Region", "Count"]

    fig_region = px.bar(
        region_freq,
        x="Region",
        y="Count",
        title="Affected Body Regions",
        color="Count",
        color_continuous_scale="Reds"
    )
    fig_region.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_region, use_container_width=True)