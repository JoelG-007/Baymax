import streamlit as st

def render_architecture():
    st.title("System Architecture")

    st.markdown("""
    ### Baymax Architecture Overview

    **1. Input Layer**
    - LLM-based intent classification
    - NLP-based symptom extraction (spaCy)
    - Negation detection

    **2. Processing Layer**
    - Rule-based emergency engine
    - Weighted risk scoring model
    - Lab parameter threshold detection
    - Anomaly & improvement detection

    **3. Intelligence Layer**
    - Controlled LLM advisory
    - Deterministic + AI hybrid design

    **4. Data Layer**
    - Structured health event storage
    - Lab parameter JSON storage
    - Timeline tracking

    **5. Output Layer**
    - Risk gauge visualization
    - Trend analytics
    - PDF health report export
    """)