from datetime import datetime, timedelta
import streamlit as st

SESSION_TIMEOUT_MINUTES = 30

def refresh_session():
    st.session_state.last_active = datetime.utcnow()

def is_session_expired():
    last = st.session_state.get("last_active")
    if not last:
        return False
    return datetime.utcnow() - last > timedelta(minutes=SESSION_TIMEOUT_MINUTES)