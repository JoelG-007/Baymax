import streamlit as st

from database.crud import get_user_by_id

from ui.dashboard import render_dashboard
from ui.chat import render_chat
from ui.timeline import render_timeline
from ui.documents import render_documents
from ui.analytics import render_analytics
from ui.parameters import render_parameters
from ui.profile import render_profile

from auth.session_manager import is_session_expired, refresh_session

def render_page():
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Please login first.")
        st.stop()

    # -----------------------
    # Mid-session suspension check
    # Re-validates on every page load
    # -----------------------
    db_user = get_user_by_id(st.session_state.user["id"])
    if not db_user or not db_user.is_active:
        st.session_state.user = None
        st.error("Your account has been suspended. Please contact support.")
        st.stop()

    # Session timeout check
    if is_session_expired():
        st.session_state.user = None
        st.session_state.last_active = None
        st.warning("Your session has expired. Please login again.")
        st.stop()
    
    # Refresh the timer on every active page load
    refresh_session()

    # Sync role in case it was changed by master mid-session
    if db_user.role != st.session_state.user["role"]:
        st.session_state.user["role"] = db_user.role
        st.rerun()

    # -----------------------
    # Sidebar Branding
    # -----------------------
    st.sidebar.markdown("""
        ## Hello, This is Baymax
        Your personal health-care companion
    """)

    st.sidebar.markdown("---")
    st.sidebar.title("Baymax")
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {st.session_state.user['username']}")

    # -----------------------
    # Navigation
    # -----------------------
    role = st.session_state.user["role"]

    if role == "user":
        pages = [
            "Dashboard",
            "Health Chat",
            "Timeline",
            "Analytics",
            "Lab Trends",
            "Documents",
            "Profile"
        ]
    elif role == "admin":
        pages = ["Admin Panel", "Profile"]
    elif role == "master":
        pages = ["Admin Panel", "Master Panel", "Profile"]
    else:
        pages = ["Profile"]

    page = st.sidebar.radio("Navigation", pages)

    st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # -----------------------
    # Page Routing
    # -----------------------
    if page == "Dashboard":
        render_dashboard()
    elif page == "Health Chat":
        render_chat()
    elif page == "Timeline":
        render_timeline()
    elif page == "Analytics":
        render_analytics()
    elif page == "Lab Trends":
        render_parameters()
    elif page == "Documents":
        render_documents()
    elif page == "Profile":
        render_profile()
    elif page == "Admin Panel":
        from ui.admin import render_admin
        render_admin()
    elif page == "Master Panel":
        from ui.master import render_master
        render_master()
    
