import streamlit as st
import json
import pandas as pd
import plotly.express as px
from database.crud import get_document_summaries

REFERENCE_RANGES = {
    "HbA1c":       "Normal: < 5.7% | Pre-diabetic: 5.7–6.4% | Diabetic: ≥ 6.5%",
    "Cholesterol":  "Normal: < 200 mg/dL | Borderline: 200–239 | High: ≥ 240",
    "Blood Sugar":  "Normal: < 140 mg/dL | Pre-diabetic: 140–199 | Diabetic: ≥ 200",
    "Glucose":      "Normal: 70–99 mg/dL (fasting) | Pre-diabetic: 100–125 | Diabetic: ≥ 126",
    "Blood Pressure": "Normal: < 120/80 mmHg | Elevated: 120–129/<80 | Hypertension: ≥ 130/80",
    "Heart Rate":   "Normal: 60–100 bpm | Bradycardia: < 60 | Tachycardia: > 100",
    "BMI":          "Underweight: < 18.5 | Normal: 18.5–24.9 | Overweight: 25–29.9 | Obese: ≥ 30",
    "Vitamin D":    "Deficient: < 20 ng/mL | Insufficient: 20–29 | Sufficient: ≥ 30",
    "WBC Count":    "Normal: 4,000–11,000 cells/µL | Leukopenia: < 4,000 | Leukocytosis: > 11,000",
    "RBC Count":    "Normal: 4.7–6.1 million cells/µL (men) | 4.2–5.4 million cells/µL (women) | Anemia: < normal range | Polycythemia: > normal range",
    "Platelet Count": "Normal: 150,000–450,000 platelets/µL | Thrombocytopenia: < 150,000 | Thrombocytosis: > 450,000",
    "eGFR":         "Normal: ≥ 90 mL/min/1.73m² | Mildly Decreased: 60–89 | Moderately Decreased: 30–59 | Severely Decreased: 15–29 | Kidney Failure: < 15",
    "ALT":          "Normal: 7–56 U/L | Elevated: > 56",
    "AST":          "Normal: 10–40 U/L | Elevated: > 40",
    "Creatinine":   "Normal: 0.84–1.21 mg/dL (men) | 0.59–1.04 mg/dL (women) | Elevated: > normal range",
    "TSH":          "Normal: 0.4–4.0 mIU/L | Hypothyroidism: > 4.0 | Hyperthyroidism: < 0.4",
    "Haemoglobin":  "Normal: 13.8–17.2 g/dL (men) | 12.1–15.1 g/dL (women) | Anemia: < normal range | Polycythemia: > normal range",
    "Platelets":    "Normal: 150,000–450,000 platelets/µL | Thrombocytopenia: < 150,000 | Thrombocytosis: > 450,000",
    "WBC":          "Normal: 4,000–11,000 cells/µL | Leukopenia: < 4,000 | Leukocytosis: > 11,000",
    "RBC":          "Normal: 4.7–6.1 million cells/µL (men) | 4.2–5.4 million cells/µL (women)",
    "MCH":                         "Normal: 27–33 pg",
    "MCHC":                        "Normal: 32–36 g/dL | Hypochromic: < 32 | Hyperchromic: > 36",
    "Mean Corpuscular Volume (MCV)": "Normal: 80–100 fL | Microcytic: < 80 | Macrocytic: > 100",
    "Neutrophils":                 "Normal: 40–70% | Neutropenia: < 40 | Neutrophilia: > 70",
    "Lymphocytes":                 "Normal: 20–40% | Lymphopenia: < 20 | Lymphocytosis: > 40",
    "Monocytes":                   "Normal: 2–8% | Monocytopenia: < 2 | Monocytosis: > 8",
    "Eosinophils":                 "Normal: 1–4% | Eosinopenia: < 1 | Eosinophilia: > 4",
    "Basophils":                   "Normal: 0–1% | Basopenia: < 0 | Basophilia: > 1",
    "CRP":          "Normal: < 3 mg/L | Elevated: ≥ 3",
    "ESR":          "Normal: < 20 mm/hr (men) | < 30 mm/hr (women)",
    "Ferritin":     "Normal: 24–336 ng/mL (men) | 11–272 ng/mL (women)",
    "D-dimer":      "Normal: < 0.5 µg/mL | Elevated: ≥ 0.5"
}


def render_parameters():
    st.title("Lab Parameter Trends")

    user_id = st.session_state.user["id"]
    docs = get_document_summaries(user_id)

    records = []

    for d in docs:
        if d.key_parameters_json:
            params = json.loads(d.key_parameters_json)
            for key, value in params.items():
                records.append({
                    "Parameter": key,
                    "Value":     value,
                    "Date":      d.created_at
                })

    if not records:
        st.info("No lab parameters found yet. Upload a medical report in Documents.")
        return

    df = pd.DataFrame(records)

    # -----------------------
    # Full Parameters Table
    # -----------------------
    st.subheader("All Extracted Parameters")

    # Pivot: one row per document date, one column per parameter
    table_df = df.copy()
    table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")
    pivot = table_df.pivot_table(
        index="Date",
        columns="Parameter",
        values="Value",
        aggfunc="first"
    ).reset_index()

    # Transpose for readability when there's only one report
    if len(pivot) == 1:
        transposed = pivot.drop(columns="Date").T.reset_index()
        transposed.columns = ["Parameter", "Value"]
        st.dataframe(transposed, use_container_width=True, hide_index=True)
    else:
        st.dataframe(pivot, use_container_width=True, hide_index=True)

    st.markdown("---")

    # -----------------------
    # Individual Parameter Trend
    # -----------------------
    st.subheader("Parameter Trend")

    parameter_selected = st.selectbox(
        "Select Parameter to Chart",
        df["Parameter"].unique()
    )

    if parameter_selected in REFERENCE_RANGES:
        st.caption(f"Reference: {REFERENCE_RANGES[parameter_selected]}")

    filtered = df[df["Parameter"] == parameter_selected]

    if len(filtered) < 2:
        st.info(f"Upload more reports to see a trend for **{parameter_selected}**.")
        st.metric(label=parameter_selected, value=filtered["Value"].iloc[0])
        return

    fig = px.line(
        filtered,
        x="Date",
        y="Value",
        markers=True,
        title=f"{parameter_selected} Trend Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)