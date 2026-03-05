import streamlit as st
import re
from auth.auth_service import authenticate, register

def render_login():
    st.title("Baymax Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------------- LOGIN TAB ----------------
    with tab1:
        login_identifier = st.text_input(
            "Username or Email",
            key="login_identifier"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", key="login_button"):
            if not login_identifier or not login_password:
                st.warning("Please enter your username and password.")
            else:
                user = authenticate(login_identifier, login_password)
                if user:
                    st.session_state.user = {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                    st.session_state.pdf_report = None        # clearing any stale report
                    st.session_state.risk_explanation = None  # clearing any stale explanation
                    st.session_state.chat_history = []        # clearing any stale chat
                    st.rerun()
                else:
                    st.error("Invalid credentials or account suspended.")

    # ---------------- REGISTER TAB ----------------
    with tab2:
        reg_username = st.text_input(
            "Username",
            key="register_username"
        )

        reg_email = st.text_input(
            "Email",
            key="register_email"
        )

        reg_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        reg_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        if st.button("Register", key="register_button"):
            if not reg_username or not reg_email or not reg_password or not reg_confirm_password:
                st.warning("Please fill in all fields.")
            elif len(reg_username.strip()) < 3:
                st.warning("Username must be at least 3 characters.")
            elif not re.match(r"^[a-zA-Z0-9_]+$", reg_username.strip()):
                st.warning("Username can only contain letters, numbers, and underscores.")
            elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", reg_email.strip()):
                st.warning("Please enter a valid email address.")
            elif len(reg_password) < 8:
                st.warning("Password must be at least 8 characters.")
            elif not re.search(r"[A-Z]", reg_password):
                st.warning("Password must contain at least one uppercase letter.")
            elif not re.search(r"[0-9]", reg_password):
                st.warning("Password must contain at least one number.")
            elif reg_password != reg_confirm_password:
                st.warning("Passwords do not match.")
            else:
                result = register(reg_username, reg_email, reg_password)
                if result == "User created successfully":
                    st.success("Registered successfully! Please login.")
                else:
                    st.error(result)