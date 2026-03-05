import streamlit as st
from database.db_init import SessionLocal
from database.models import User, HealthEvent, Document, AdminAudit, LoginAudit
from core.ai_layer import generate_advisory
import time


def render_admin():

    if st.session_state.user["role"] not in ["admin", "master"]:
        st.error("Unauthorized")
        st.stop()

    st.title("Admin Control Panel")

    db = SessionLocal()

    try:
        section = st.selectbox(
            "Select Section",
            ["Users", "Health Events", "Documents", "Login Audit", "API Monitor"]
        )

        # ---------------- USERS ----------------
        if section == "Users":

            users = db.query(User).all()

            if not users:
                st.info("No users found.")
            else:
                col_h1, col_h2, col_h3, col_h4 = st.columns([2, 2, 2, 2])
                col_h1.markdown("**Username**")
                col_h2.markdown("**Role**")
                col_h3.markdown("**Status**")
                col_h4.markdown("**Action**")

                for user in users:
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    col1.write(user.username)
                    col2.write(user.role)
                    col3.write("Active" if user.is_active else "Suspended")

                    current_role = st.session_state.user["role"]
                    current_id   = st.session_state.user["id"]

                    can_modify = True
                    if current_role == "admin":
                        if user.role in ["master", "admin"] or user.id == current_id:
                            can_modify = False

                    if can_modify:
                        label = "Suspend" if user.is_active else "Activate"
                        if col4.button(label, key=f"suspend_{user.id}"):
                            old_status = user.is_active
                            user.is_active = 0 if user.is_active else 1
                            db.add(AdminAudit(
                                admin_id=current_id,
                                target_table="User",
                                target_id=user.id,
                                field_changed="is_active",
                                old_value=str(old_status),
                                new_value=str(user.is_active)
                            ))
                            db.commit()
                            st.success("User status updated.")
                            st.rerun()
                    else:
                        col4.write("Protected")

        # ---------------- HEALTH EVENTS ----------------
        elif section == "Health Events":

            st.warning(
                "You are viewing sensitive patient health data. "
                "Handle with care and only action when necessary."
            )

            events = db.query(HealthEvent).all()

            if not events:
                st.info("No health events found.")
            else:
                col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([1, 2, 2, 2, 2])
                col_h1.markdown("**ID**")
                col_h2.markdown("**User ID**")
                col_h3.markdown("**Symptom**")
                col_h4.markdown("**Severity**")
                col_h5.markdown("**Action**")

                for event in events:
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
                    col1.write(event.id)
                    col2.write(event.user_id)
                    col3.write(event.symptom)
                    col4.write(event.severity)

                    if col5.button("Delete", key=f"delete_event_{event.id}"):
                        db.add(AdminAudit(
                            admin_id=st.session_state.user["id"],
                            target_table="HealthEvent",
                            target_id=event.id,
                            field_changed="delete",
                            old_value="exists",
                            new_value="deleted"
                        ))
                        db.delete(event)
                        db.commit()
                        st.success("Deleted & logged.")
                        st.rerun()

        # ---------------- DOCUMENTS ----------------
        elif section == "Documents":

            documents = db.query(Document).all()

            if not documents:
                st.info("No documents found.")
            else:
                col_h1, col_h2, col_h3, col_h4 = st.columns([1, 2, 3, 2])
                col_h1.markdown("**ID**")
                col_h2.markdown("**User ID**")
                col_h3.markdown("**Filename**")
                col_h4.markdown("**Action**")

                for doc in documents:
                    col1, col2, col3, col4 = st.columns([1, 2, 3, 2])
                    col1.write(doc.id)
                    col2.write(doc.user_id)
                    col3.write(doc.original_filename)

                    if col4.button("Delete", key=f"delete_doc_{doc.id}"):
                        db.add(AdminAudit(
                            admin_id=st.session_state.user["id"],
                            target_table="Document",
                            target_id=doc.id,
                            field_changed="delete",
                            old_value="exists",
                            new_value="deleted"
                        ))
                        db.delete(doc)
                        db.commit()
                        st.success("Deleted & logged.")
                        st.rerun()

        # ---------------- LOGIN AUDIT ----------------
        elif section == "Login Audit":

            st.subheader("Login Attempt History")

            attempts = db.query(LoginAudit).order_by(
                LoginAudit.timestamp.desc()
            ).limit(100).all()

            if not attempts:
                st.info("No login attempts recorded yet.")
            else:
                col_h1, col_h2, col_h3 = st.columns([3, 2, 2])
                col_h1.markdown("**Identifier**")
                col_h2.markdown("**Result**")
                col_h3.markdown("**Timestamp**")

                for attempt in attempts:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    col1.write(attempt.identifier)
                    if attempt.success:
                        col2.success("Success")
                    else:
                        col2.error("Failed")
                    col3.write(attempt.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        # ---------------- API MONITOR ----------------
        elif section == "API Monitor":

            st.subheader("Groq API Health Check")

            if st.button("Test API Connectivity"):
                try:
                    start = time.time()
                    generate_advisory(
                        {"symptom": "test", "severity": "Mild", "body_region": "General"},
                        st.session_state.user["id"]
                    )
                    latency = round(time.time() - start, 2)
                    st.success(f"API Connected | Latency: {latency}s")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")

    finally:
        db.close()