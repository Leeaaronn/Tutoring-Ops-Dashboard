"""Tutoring Ops Dashboard — Streamlit entry point."""

import sqlite3
from pathlib import Path

import streamlit as st

from dashboard.data.metrics import (
    at_risk_students,
    avg_attendance_rate,
    no_show_rate,
    tutor_utilization,
)

WEEK_START = "2024-01-15"
DB_PATH = Path.cwd() / "data" / "warehouse.db"
HIGH_UTIL_THRESHOLD = 0.85

st.set_page_config(
    page_title="Tutoring Ops Dashboard",
    page_icon="📚",
    layout="wide",
)

st.title("Tutoring Ops Dashboard")
st.caption(f"Week of {WEEK_START}")

if not DB_PATH.exists():
    st.error(f"Database not found at: {DB_PATH}")
    st.info("Run: uv run python -m dashboard.data.load_sqlite")
    st.stop()

subject = st.selectbox(
    "Compute no-show rate for",
    ["Computer Science", "Math", "English"],
)

conn = sqlite3.connect(str(DB_PATH))
try:
    attendance = avg_attendance_rate(conn, WEEK_START)
    selected_no_show = no_show_rate(conn, subject, WEEK_START)
    utilization = tutor_utilization(conn, WEEK_START)
    at_risk = at_risk_students(conn, WEEK_START)
finally:
    conn.close()

high_util = [(name, u) for name, u in utilization.items() if u > HIGH_UTIL_THRESHOLD]
high_util_count = len(high_util)
util_rows = sorted(utilization.items(), key=lambda x: x[1], reverse=True)

# ── KPIs ────────────────────────────────────────────────────────────────────
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

    c1.metric("Avg Attendance", f"{attendance:.0%}")
    c2.metric(
        f"{subject} No-Show",
        f"{selected_no_show:.0%}" if selected_no_show is not None else "N/A",
    )
    c3.metric(f"High Util Tutors (>{HIGH_UTIL_THRESHOLD:.0%})", high_util_count)
    c4.metric("At-Risk Students", len(at_risk))

if high_util_count > 0:
    names = ", ".join(sorted(name for name, _ in high_util))
    st.warning(
        f"Capacity tight: {high_util_count} tutor(s) are above "
        f"{HIGH_UTIL_THRESHOLD:.0%} utilization ({names})."
    )
else:
    st.success("Capacity looks healthy this week.")

st.divider()

# ── Detail section ──────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("Tutor Utilization")

        for name, util in util_rows:
            row_left, row_right = st.columns([1, 3])
            with row_left:
                st.write(f"**{name}**")
                st.caption(f"{util:.0%}")
            with row_right:
                st.progress(min(int(util * 100), 100))

with right:
    with st.container(border=True):
        st.subheader("At-Risk Students")

        if at_risk:
            st.dataframe(
                [{"Student": s} for s in at_risk],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.write("None")
