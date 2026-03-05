import streamlit as st
from database.db_init import SessionLocal
from database.models import User, RoleAudit, AdminAudit, LoginAudit


def render_master():

    if st.session_state.user["role"] != "master":
        st.error("Unauthorized")
        st.stop()

    st.title("Master Control Panel")

    db = SessionLocal()

    try:
        section = st.selectbox(
            "Select Section",
            ["Role Management", "Admin Activity Logs", "Login Audit"]
        )

        # ---------------- ROLE MANAGEMENT ----------------
        if section == "Role Management":

            st.subheader("Manage Admin Roles")

            users = db.query(User).all()

            col_h1, col_h2, col_h3 = st.columns([2, 2, 2])
            col_h1.markdown("**Username**")
            col_h2.markdown("**Role**")
            col_h3.markdown("**Action**")

            for user in users:
                col1, col2, col3 = st.columns([2, 2, 2])
                col1.write(user.username)
                col2.write(user.role)

                if user.role == "user":
                    if col3.button("Promote to Admin", key=f"promote_{user.id}"):
                        user.role = "admin"
                        db.add(RoleAudit(
                            changed_user_id=user.id,
                            changed_by=st.session_state.user["id"],
                            new_role="admin"
                        ))
                        db.commit()
                        st.success(f"{user.username} promoted to admin.")
                        st.rerun()

                elif user.role == "admin" and user.id != st.session_state.user["id"]:
                    if col3.button("Revoke Admin", key=f"revoke_{user.id}"):
                        user.role = "user"
                        db.add(RoleAudit(
                            changed_user_id=user.id,
                            changed_by=st.session_state.user["id"],
                            new_role="user"
                        ))
                        db.commit()
                        st.success(f"{user.username} revoked to user.")
                        st.rerun()

                elif user.role == "master":
                    col3.write("Protected")

        # ---------------- ADMIN ACTIVITY LOGS ----------------
        elif section == "Admin Activity Logs":

            st.subheader("Admin Activity Logs")

            audits = db.query(AdminAudit).order_by(
                AdminAudit.timestamp.desc()
            ).all()

            if not audits:
                st.info("No admin activity yet.")
            else:
                col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([1, 2, 2, 2, 2])
                col_h1.markdown("**Admin ID**")
                col_h2.markdown("**Table**")
                col_h3.markdown("**Record ID**")
                col_h4.markdown("**Change**")
                col_h5.markdown("**Timestamp**")

                for audit in audits:
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
                    col1.write(audit.admin_id)
                    col2.write(audit.target_table)
                    col3.write(audit.target_id)
                    col4.write(
                        f"{audit.field_changed}: "
                        f"{audit.old_value} → {audit.new_value}"
                    )
                    col5.write(audit.timestamp.strftime("%Y-%m-%d %H:%M"))

        # ---------------- LOGIN AUDIT ----------------
        elif section == "Login Audit":

            st.subheader("Login Attempt History")

            attempts = db.query(LoginAudit).order_by(
                LoginAudit.timestamp.desc()
            ).limit(200).all()

            if not attempts:
                st.info("No login attempts recorded yet.")
            else:
                # Summary metrics
                total     = len(attempts)
                successes = sum(1 for a in attempts if a.success)
                failures  = total - successes

                col1, col2, col3 = st.columns(3)
                col1.metric(f"**Total Attempts**\n\n### {total}")
                col2.metric(f"**Successful**\n\n###{successes}")
                col3.metric(f"**Failed**\n\n###{failures}")

                st.markdown("---")

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

    finally:
        db.close()