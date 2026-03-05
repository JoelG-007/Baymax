import streamlit as st
from auth.security import hash_password, verify_password
from database.crud import (
    get_user_by_id,
    update_user_password,
    update_user_email,
    delete_user_account
)


def render_profile():
    st.title("My Profile")

    user_id = st.session_state.user["id"]
    user = get_user_by_id(user_id)

    if not user:
        st.error("User not found.")
        return

    # -----------------------
    # Account Info
    # -----------------------
    st.subheader("Account Info")

    col1, col2 = st.columns(2)
    col1.markdown(f"**Username**\n\n### {user.username}")
    col2.markdown(f"**Role**\n\n### {user.role.capitalize()}")

    st.markdown("---")

    # -----------------------
    # Change Email
    # -----------------------
    st.subheader("Change Email")

    new_email = st.text_input(
        "New Email",
        placeholder=user.email,
        key="new_email"
    )

    if st.button("Update Email"):
        if not new_email:
            st.warning("Please enter a new email address.")
        elif new_email.strip().lower() == user.email:
            st.warning("That's already your current email.")
        else:
            result = update_user_email(user_id, new_email)
            if result == "Email updated successfully":
                st.session_state.user["email"] = new_email.strip().lower()
                st.success("Email updated successfully.")
            else:
                st.error(result)

    st.markdown("---")

    # -----------------------
    # Change Password
    # -----------------------
    st.subheader("Change Password")

    current_password = st.text_input(
        "Current Password",
        type="password",
        key="current_password"
    )
    new_password = st.text_input(
        "New Password",
        type="password",
        key="new_password"
    )
    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="confirm_password"
    )

    if st.button("Update Password"):
        if not current_password or not new_password or not confirm_password:
            st.warning("Please fill in all password fields.")
        elif not verify_password(current_password, user.hashed_password):
            st.error("Current password is incorrect.")
        elif new_password != confirm_password:
            st.error("New passwords do not match.")
        elif len(new_password) < 6:
            st.warning("Password must be at least 6 characters.")
        else:
            update_user_password(user_id, hash_password(new_password))
            st.success("Password updated successfully.")

    st.markdown("---")

    # -----------------------
    # Delete Account
    # -----------------------
    st.subheader("Delete Account")
    st.warning(
        "⚠️ Deleting your account is permanent. "
        "All your symptoms, documents, and health data will be erased."
    )

    confirm_delete = st.text_input(
        "Type your username to confirm deletion",
        key="confirm_delete"
    )

    if st.button("Delete My Account", type="primary"):
        if confirm_delete != user.username:
            st.error("Username does not match. Deletion cancelled.")
        else:
            delete_user_account(user_id)
            st.session_state.user = None
            st.success("Account deleted.")
            st.rerun()