import streamlit as st
import plotly.graph_objects as go
from core.timeline_engine import get_combined_timeline
from database.crud import get_health_events, resolve_health_event


def render_timeline():
    st.title("Health Timeline")

    user_id = st.session_state.user["id"]
    events = get_combined_timeline(user_id)

    # -----------------------
    # Timeline Chart
    # -----------------------
    if not events:
        st.info("No events logged yet.")
    else:
        x = [e["timestamp"] for e in events]
        y = list(range(len(events)))
        colors = ["#3498db" if e["type"] == "Symptom" else "#9b59b6" for e in events]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers+text",
            marker=dict(size=12, color=colors),
            text=[e["type"] for e in events],
            textposition="top center",
            customdata=[e["description"] or "No detail" for e in events],
            hovertemplate="<b>%{text}</b><br>%{x}<br>%{customdata}<extra></extra>",
            showlegend=False
        ))

        # Legend-only invisible traces for color key
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(color="#3498db", size=10), name="Symptom"
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(color="#9b59b6", size=10), name="Document"
        ))

        fig.update_layout(
            height=500,
            showlegend=True,
            yaxis=dict(showticklabels=False),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right",  x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------
    # Active Symptoms — Mark as Resolved
    # -----------------------
    st.markdown("---")
    st.subheader("Active Symptoms")

    all_events = get_health_events(user_id)
    active = [e for e in all_events if not e.is_resolved]

    if not active:
        st.success("No active symptoms. All clear!")
    else:
        col_h1, col_h2, col_h3, col_h4 = st.columns([3, 2, 2, 2])
        col_h1.markdown("**Symptom**")
        col_h2.markdown("**Severity**")
        col_h3.markdown("**Logged On**")
        col_h4.markdown("**Action**")

        for e in active:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(e.symptom)
            col2.write(e.severity)
            col3.write(e.timestamp.strftime("%Y-%m-%d"))
            if col4.button("Mark Resolved ✓", key=f"resolve_{e.id}"):
                resolve_health_event(e.id, user_id)
                st.rerun()

    # -----------------------
    # Resolved Symptoms (collapsed)
    # -----------------------
    resolved = [e for e in all_events if e.is_resolved]

    if resolved:
        with st.expander(f"View resolved symptoms ({len(resolved)})"):
            for e in resolved:
                resolved_date = (
                    e.resolved_at.strftime("%Y-%m-%d") if e.resolved_at else "N/A"
                )
                st.write(
                    f"**{e.symptom}** ({e.severity}) — resolved {resolved_date}"
                )