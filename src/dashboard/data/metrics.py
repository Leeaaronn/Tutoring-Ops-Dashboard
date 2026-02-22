"""Metric queries for the tutoring ops dashboard.

All functions accept an open sqlite3.Connection and a week_start ISO date string
(Monday). Week range:
    session_date >= week_start AND session_date < week_start + 7 days
"""

import sqlite3


def avg_attendance_rate(conn: sqlite3.Connection, week_start: str) -> float:
    row = conn.execute(
        """
        SELECT AVG(CAST(attended AS REAL) / scheduled)
        FROM (
            SELECT
                student_id,
SUM(
    CASE WHEN status IN ('present','late') THEN 1 ELSE 0 END
) AS attended,
SUM(
    CASE WHEN status IN ('present','late','no_show') THEN 1 ELSE 0 END
) AS scheduled
            FROM sessions
            WHERE session_date >= ?
              AND session_date < date(?, '+7 days')
            GROUP BY student_id
            HAVING scheduled > 0
        )
        """,
        (week_start, week_start),
    ).fetchone()
    return float(row[0] or 0.0)


def no_show_rate(
    conn: sqlite3.Connection, subject_name: str, week_start: str
) -> float | None:
    row = conn.execute(
        """
        SELECT
            SUM(CASE WHEN s.status = 'no_show' THEN 1 ELSE 0 END),
            COUNT(*)
        FROM sessions s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.name = ?
          AND s.session_date >= ?
          AND s.session_date < date(?, '+7 days')
        """,
        (subject_name, week_start, week_start),
    ).fetchone()
    no_show_count, scheduled_count = row
    if not scheduled_count:
        return None
    return no_show_count / scheduled_count


def tutor_utilization(conn: sqlite3.Connection, week_start: str) -> dict[str, float]:
    rows = conn.execute(
        """
        SELECT
            t.name,
            t.available_hours_per_week,
            COALESCE(SUM(s.scheduled_hours), 0.0) AS booked_hours
        FROM tutors t
        LEFT JOIN sessions s
            ON t.tutor_id = s.tutor_id
           AND s.session_date >= ?
           AND s.session_date < date(?, '+7 days')
        GROUP BY t.tutor_id, t.name, t.available_hours_per_week
        """,
        (week_start, week_start),
    ).fetchall()
    return {name: booked / available for name, available, booked in rows}


def at_risk_students(conn: sqlite3.Connection, week_start: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT st.name
        FROM student_progress sp
        JOIN students st ON sp.student_id = st.student_id
        WHERE sp.week_start = ?
          AND sp.progress_percent < 60
        ORDER BY st.name
        """,
        (week_start,),
    ).fetchall()
    return [row[0] for row in rows]
