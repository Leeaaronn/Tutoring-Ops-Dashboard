"""Tutoring Ops Dashboard — Streamlit entry point."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.data.metrics import (
    at_risk_students,
    avg_attendance_rate,
    no_show_rate,
    tutor_utilization,
)

REPO_ROOT = Path(__file__).resolve().parents[2]  # src/dashboard/app.py -> repo root
DB_PATH = REPO_ROOT / "data" / "warehouse.db"

HIGH_UTIL_THRESHOLD = 0.85
SUBJECTS = ["Computer Science", "Math", "English"]


def available_weeks(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT week_start
        FROM student_progress
        ORDER BY week_start DESC
        """
    ).fetchall()
    return [r[0] for r in rows]


def attendance_trend(conn: sqlite3.Connection) -> list[tuple[str, float]]:
    # Compute Monday week_start from sessions.session_date (SQLite).
    # strftime('%w') gives 0=Sun..6=Sat. Convert to "days since Monday" and subtract.
    rows = conn.execute(
        """
        WITH sessions_with_week AS (
            SELECT
                date(
                    session_date,
                    printf(
                        '-%d days',
                        (CAST(strftime('%w', session_date) AS INTEGER) + 6) % 7
                    )
                ) AS week_start,
                status
            FROM sessions
            WHERE status IN ('present', 'late', 'no_show')
        )
        SELECT
            week_start,
            AVG(CASE WHEN status IN ('present', 'late') THEN 1.0 ELSE 0.0 END) AS rate
        FROM sessions_with_week
        GROUP BY week_start
        ORDER BY week_start
        """
    ).fetchall()
    return [(r[0], float(r[1])) for r in rows]


st.set_page_config(
    page_title="Tutoring Ops Dashboard",
    page_icon="📚",
    layout="wide",
)

st.title("Tutoring Ops Dashboard")
st.caption("Operational metrics for your tutoring business.")

if not DB_PATH.exists():
    st.error(f"Database not found at: {DB_PATH}")
    st.info("Run: uv run python -m dashboard.data.load_sqlite")
    st.stop()

# Filters (top)
subject = st.selectbox("Compute no-show rate for", SUBJECTS, index=0)

with sqlite3.connect(str(DB_PATH)) as conn:
    conn.execute("PRAGMA foreign_keys = ON")

    weeks = available_weeks(conn)
    if not weeks:
        st.error("No weeks available in student_progress.")
        st.stop()

    if len(weeks) == 1:
        week_start = weeks[0]
        st.caption(f"Week of {week_start}")
    else:
        week_start = st.selectbox(
            "Week starting (Monday)",
            weeks,
            index=0,
            help="Weeks are populated from student_progress.week_start.",
        )

    attendance = avg_attendance_rate(conn, week_start)
    selected_no_show = no_show_rate(conn, subject, week_start)
    utilization = tutor_utilization(conn, week_start)
    at_risk = at_risk_students(conn, week_start)

    trend_rows = attendance_trend(conn)

high_util = [(name, u) for name, u in utilization.items() if u > HIGH_UTIL_THRESHOLD]
high_util_count = len(high_util)
util_rows = sorted(utilization.items(), key=lambda x: x[1], reverse=True)

# KPIs
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

# Trend chart (only if we have >= 2 weeks)
if len(trend_rows) >= 2:
    st.subheader("Attendance Trend")
    df = pd.DataFrame(trend_rows, columns=["week_start", "attendance_rate"]).set_index(
        "week_start"
    )
    st.line_chart(df, height=220)
    st.divider()

# Detail section
left, right = st.columns(2, gap="large")

with left, st.container(border=True):
    st.subheader("Tutor Utilization")
    for name, util in util_rows:
        row_left, row_right = st.columns([1, 3])
        with row_left:
            st.write(f"**{name}**")
            st.caption(f"{util:.0%}")
        with row_right:
            st.progress(min(int(util * 100), 100))

with right, st.container(border=True):
    st.subheader("At-Risk Students")
    if at_risk:
        st.dataframe(
            [{"Student": s} for s in at_risk],
            hide_index=True,
            width="stretch",
        )
    else:
        st.write("None")
