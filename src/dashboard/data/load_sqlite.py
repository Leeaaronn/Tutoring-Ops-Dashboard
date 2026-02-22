"""Load data/*.csv into data/warehouse.db (SQLite).

Run:
    uv run python -m dashboard.data.load_sqlite
"""

import csv
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "warehouse.db"

TABLES = ["subjects", "tutors", "students", "sessions", "student_progress"]

INT_COLS = {"subject_id", "tutor_id", "student_id", "session_id", "progress_id"}
FLOAT_COLS = {"available_hours_per_week", "scheduled_hours", "progress_percent"}

_DDL = """\
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE
);

CREATE TABLE tutors (
    tutor_id                 INTEGER PRIMARY KEY,
    name                     TEXT    NOT NULL UNIQUE,
    available_hours_per_week REAL    NOT NULL CHECK (available_hours_per_week > 0)
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE
);

CREATE TABLE sessions (
    session_id      INTEGER PRIMARY KEY,
    student_id      INTEGER NOT NULL,
    tutor_id        INTEGER NOT NULL,
    subject_id      INTEGER NOT NULL,
    session_date    TEXT    NOT NULL,
    scheduled_hours REAL    NOT NULL CHECK (scheduled_hours > 0),
    status          TEXT    NOT NULL
                CHECK (status IN ('present','late','no_show','cancelled')),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
    FOREIGN KEY (tutor_id)   REFERENCES tutors(tutor_id)     ON DELETE RESTRICT,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE RESTRICT
);

CREATE TABLE student_progress (
    progress_id      INTEGER PRIMARY KEY,
    student_id       INTEGER NOT NULL,
    week_start       TEXT    NOT NULL,
    progress_percent REAL    NOT NULL
                 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
    UNIQUE (student_id, week_start)
);

CREATE INDEX idx_sessions_student ON sessions(student_id);
CREATE INDEX idx_sessions_tutor   ON sessions(tutor_id);
CREATE INDEX idx_sessions_subject ON sessions(subject_id);
CREATE INDEX idx_sessions_date    ON sessions(session_date);
CREATE INDEX idx_progress_student ON student_progress(student_id);
CREATE INDEX idx_progress_week    ON student_progress(week_start);
"""


def _coerce(col: str, val: str) -> int | float | str:
    if col in INT_COLS:
        return int(val)
    if col in FLOAT_COLS:
        return float(val)
    return val


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [{col: _coerce(col, v) for col, v in row.items()} for row in rows]


def _ensure_csvs() -> None:
    missing = [t for t in TABLES if not (DATA_DIR / f"{t}.csv").exists()]
    if not missing:
        return
    from dashboard.data.generate_fake_data import get_fake_data, write_csvs

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_csvs(get_fake_data(), DATA_DIR)


def _insert(conn: sqlite3.Connection, table: str, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    placeholders = ", ".join("?" * len(cols))
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"  # noqa: S608
    conn.executemany(sql, [tuple(r[c] for c in cols) for r in rows])


def main() -> None:
    _ensure_csvs()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(_DDL)
        conn.execute("PRAGMA foreign_keys = ON")

        for table in TABLES:
            rows = _read_csv(DATA_DIR / f"{table}.csv")
            _insert(conn, table, rows)
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608
            print(f"  {table}: {count} rows")

        conn.commit()
    finally:
        conn.close()

    print(f"Loaded {DB_PATH}")


if __name__ == "__main__":
    main()
