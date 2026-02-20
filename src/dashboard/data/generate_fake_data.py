"""Generate deterministic fake data for the tutoring ops dashboard.

Run as a script to write CSVs to the project-level data/ directory:
    python -m dashboard.data.generate_fake_data

Or import get_fake_data() for use in tests and load_sqlite.py.
"""

import csv
from pathlib import Path

WEEK_START = "2024-01-15"

# ── Reference data ─────────────────────────────────────────────────────────────

SUBJECTS = [
    {"subject_id": 1, "name": "Math"},
    {"subject_id": 2, "name": "Computer Science"},
    {"subject_id": 3, "name": "English"},
]

TUTORS = [
    {"tutor_id": 1, "name": "Tutor_A", "available_hours_per_week": 20.0},
    {"tutor_id": 2, "name": "Tutor_B", "available_hours_per_week": 20.0},
    {"tutor_id": 3, "name": "Tutor_C", "available_hours_per_week": 15.0},
]

STUDENTS = [{"student_id": i, "name": f"Student_{i:02d}"} for i in range(1, 11)]

# ── Sessions (40 rows) ─────────────────────────────────────────────────────────
# Business truths baked in:
# - Avg attendance = 0.85
# - CS no_show = 1/10
# - Tutor_A = 18/20 hrs (0.90)
# - Tutor_C = 13/15 hrs (0.867)

_SESSION_ROWS = [
    (1, 1, 2, "2024-01-15", 1.0, "no_show"),
    (1, 1, 1, "2024-01-16", 1.0, "present"),
    (1, 1, 1, "2024-01-17", 1.0, "present"),
    (1, 1, 3, "2024-01-18", 1.0, "present"),
    (2, 1, 2, "2024-01-15", 1.0, "present"),
    (2, 1, 1, "2024-01-16", 1.0, "no_show"),
    (2, 1, 1, "2024-01-17", 1.0, "present"),
    (2, 1, 3, "2024-01-18", 1.0, "present"),
    (3, 1, 2, "2024-01-15", 1.0, "present"),
    (3, 1, 1, "2024-01-16", 1.0, "no_show"),
    (3, 1, 1, "2024-01-17", 1.0, "present"),
    (3, 1, 3, "2024-01-18", 1.0, "present"),
    (4, 1, 2, "2024-01-15", 1.0, "present"),
    (4, 1, 1, "2024-01-16", 1.0, "present"),
    (4, 1, 3, "2024-01-17", 1.0, "no_show"),
    (4, 1, 1, "2024-01-18", 1.0, "present"),
    (5, 1, 2, "2024-01-15", 1.0, "late"),
    (5, 1, 1, "2024-01-16", 1.0, "no_show"),
    (5, 2, 1, "2024-01-17", 1.0, "present"),
    (5, 2, 3, "2024-01-18", 1.0, "present"),
    (6, 2, 2, "2024-01-15", 1.0, "present"),
    (6, 2, 1, "2024-01-16", 1.0, "present"),
    (6, 2, 3, "2024-01-17", 1.0, "no_show"),
    (6, 2, 1, "2024-01-18", 1.0, "present"),
    (7, 2, 2, "2024-01-16", 1.0, "present"),
    (7, 2, 1, "2024-01-17", 1.0, "present"),
    (7, 2, 1, "2024-01-18", 1.0, "present"),
    (7, 3, 3, "2024-01-19", 1.0, "present"),
    (8, 3, 2, "2024-01-16", 1.0, "late"),
    (8, 3, 1, "2024-01-17", 1.0, "present"),
    (8, 3, 1, "2024-01-18", 1.0, "present"),
    (8, 3, 3, "2024-01-19", 1.0, "present"),
    (9, 3, 2, "2024-01-16", 1.0, "present"),
    (9, 3, 1, "2024-01-17", 1.0, "present"),
    (9, 3, 1, "2024-01-18", 1.0, "late"),
    (9, 3, 3, "2024-01-19", 1.0, "present"),
    (10, 3, 2, "2024-01-16", 1.0, "present"),
    (10, 3, 1, "2024-01-17", 1.0, "present"),
    (10, 3, 1, "2024-01-18", 1.0, "present"),
    (10, 3, 3, "2024-01-19", 1.0, "present"),
]

_PROGRESS_ROWS = [
    (1, WEEK_START, 45.0),
    (2, WEEK_START, 62.0),
    (3, WEEK_START, 75.0),
    (4, WEEK_START, 55.0),
    (5, WEEK_START, 70.0),
    (6, WEEK_START, 65.0),
    (7, WEEK_START, 80.0),
    (8, WEEK_START, 88.0),
    (9, WEEK_START, 72.0),
    (10, WEEK_START, 90.0),
]


def get_fake_data() -> dict:
    sessions = []
    for i, row in enumerate(_SESSION_ROWS, 1):
        student_id, tutor_id, subject_id, session_date, scheduled_hours, status = row
        sessions.append(
            {
                "session_id": i,
                "student_id": student_id,
                "tutor_id": tutor_id,
                "subject_id": subject_id,
                "session_date": session_date,
                "scheduled_hours": scheduled_hours,
                "status": status,
            }
        )

    progress = []
    for i, row in enumerate(_PROGRESS_ROWS, 1):
        student_id, week_start, progress_percent = row
        progress.append(
            {
                "progress_id": i,
                "student_id": student_id,
                "week_start": week_start,
                "progress_percent": progress_percent,
            }
        )

    return {
        "subjects": SUBJECTS,
        "tutors": TUTORS,
        "students": STUDENTS,
        "sessions": sessions,
        "student_progress": progress,
    }


def write_csvs(data: dict, out_dir: Path) -> None:
    for table_name, rows in data.items():
        if not rows:
            continue
        path = out_dir / f"{table_name}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    # src/dashboard/data/... -> parents[3] resolves to repository root
    out_dir = Path(__file__).resolve().parents[3] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = get_fake_data()
    write_csvs(data, out_dir)
    print(f"CSVs written to {out_dir}")


if __name__ == "__main__":
    main()
