import streamlit as st
from core.symptom_extractor import extract_symptom
from core.rule_engine import check_emergency
from core.ai_layer import generate_advisory, generate_contextual_reply, classify_intent
from database.crud import save_health_event, get_active_health_events
from core.risk_engine import calculate_risk_score


def render_chat():
    st.title("Health Chat")

    user_id = st.session_state.user["id"]

    # -----------------------
    # Chat Styling
    # -----------------------
    st.markdown("""
    <style>
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------
    # Sidebar — health context
    # -----------------------
    risk_score, risk_level = calculate_risk_score(user_id)
    active_symptoms = get_active_health_events(user_id)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Your Health Snapshot")
    st.sidebar.metric("Risk Score", f"{risk_score}/100")
    st.sidebar.metric("Active Symptoms", len(active_symptoms))
    st.sidebar.markdown("---")

    if st.sidebar.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()

    # -----------------------
    # Initialize chat history
    # -----------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -----------------------
    # Display previous messages
    # -----------------------
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -----------------------
    # Chat input
    # -----------------------
    user_input = st.chat_input(
        "Describe symptoms, ask about your reports, or ask a follow-up..."
    )

    if user_input:

        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        # -----------------------
        # Intent Classification
        # -----------------------
        intent = classify_intent(user_input)

        # -----------------------
        # Greeting — no DB write
        # -----------------------
        if intent == "greeting":
            if len(st.session_state.chat_history) <= 1:
                # First message — full intro
                reply = (
                    "Hello! I'm Baymax, your health intelligence assistant.\n\n"
                    "You can describe symptoms, ask about your uploaded medical "
                    "documents, or continue from where we left off."
                )
            else:
                # Mid-conversation greeting — short acknowledgement
                reply = "I'm here. Feel free to describe any symptoms or ask a question."
        
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            return

        # -----------------------
        # Unclear — no DB write
        # -----------------------
        if intent == "unclear":
            reply = (
                "I'm not sure I understood that.\n\n"
                "You can:\n"
                "- Describe any symptoms you are experiencing\n"
                "- Ask about your uploaded medical reports\n"
                "- Ask a follow-up question about something we already discussed"
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": reply}
            )
            with st.chat_message("assistant"):
                st.markdown(reply)
            return

        # -----------------------
        # Document query — no DB write
        # -----------------------
        if intent == "document_query":
            with st.chat_message("assistant"):
                with st.spinner("Baymax is reviewing your documents..."):
                    response = generate_contextual_reply(
                        user_input, user_id, st.session_state.chat_history
                    )
                st.markdown(response)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )
            return

        # -----------------------
        # Follow-up — no DB write
        # -----------------------
        if intent == "followup":
            with st.chat_message("assistant"):
                with st.spinner("Baymax is thinking..."):
                    response = generate_contextual_reply(
                        user_input, user_id, st.session_state.chat_history
                    )
                st.markdown(response)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )
            return

        # -----------------------
        # Symptom — extract + DB write
        # -----------------------
        record = extract_symptom(user_input)

        if check_emergency(record):
            emergency_msg = (
                "**Emergency detected.**\n\n"
                "Please call emergency services **(112)** or go to "
                "the nearest hospital immediately.\n\n"
                "Do not wait or self-medicate."
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": emergency_msg}
            )
            with st.chat_message("assistant"):
                st.error(emergency_msg)
            return

        with st.chat_message("assistant"):
            with st.spinner("Baymax is analyzing your symptoms..."):
                response = generate_advisory(
                    record, user_id, st.session_state.chat_history
                )
            st.markdown(response)

        last_message = st.session_state.chat_history[-1]["content"]
        save_health_event(user_id, record)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )