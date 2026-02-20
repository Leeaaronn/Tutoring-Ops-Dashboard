# Data Model

## Overview

Five tables. All IDs are integers. Designed for SQLite; column types and constraints are Postgres-compatible.

**ID scheme:** Every primary key is a plain integer (1, 2, 3 … N). Labels like "s01–s10" or "T1/T2/T3" are shorthand used in documentation only; the database stores integers.

---

## Tables

### `subjects`

Lookup table for tutoring subjects.

| Column | Type | Constraints |
|---|---|---|
| `subject_id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL, UNIQUE |

---

### `tutors`

One row per tutor. `available_hours_per_week` is the tutor's contracted weekly capacity.

| Column | Type | Constraints |
|---|---|---|
| `tutor_id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL, UNIQUE |
| `available_hours_per_week` | REAL | NOT NULL, CHECK (available_hours_per_week > 0) |

---

### `students`

One row per student. Names are anonymised (e.g. "Student_01").

| Column | Type | Constraints |
|---|---|---|
| `student_id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL, UNIQUE |

---

### `sessions`

One row per scheduled session. A session is always 1 hour (`scheduled_hours = 1.0`).

| Column | Type | Constraints |
|---|---|---|
| `session_id` | INTEGER | PRIMARY KEY |
| `student_id` | INTEGER | NOT NULL |
| `tutor_id` | INTEGER | NOT NULL |
| `subject_id` | INTEGER | NOT NULL |
| `session_date` | TEXT | NOT NULL (ISO-8601: YYYY-MM-DD) |
| `scheduled_hours` | REAL | NOT NULL, CHECK (scheduled_hours > 0) |
| `status` | TEXT | NOT NULL, CHECK (status IN ('present','late','no_show','cancelled')) |

**Foreign keys (CREATE TABLE constraints):**

```sql
FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
FOREIGN KEY (tutor_id)   REFERENCES tutors(tutor_id)     ON DELETE RESTRICT,
FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE RESTRICT
```

**Status semantics:**

| Status | Counts as attended? | Counts as scheduled? |
|---|---|---|
| `present` | Yes | Yes |
| `late` | Yes | Yes |
| `no_show` | No | Yes |
| `cancelled` | No | Yes |

---

### `student_progress`

One row per student per week. Tracks cumulative progress as of that week start.

| Column | Type | Constraints |
|---|---|---|
| `progress_id` | INTEGER | PRIMARY KEY |
| `student_id` | INTEGER | NOT NULL |
| `week_start` | TEXT | NOT NULL (ISO-8601: YYYY-MM-DD, must be a Monday) |
| `progress_percent` | REAL | NOT NULL, CHECK (progress_percent >= 0 AND progress_percent <= 100) |

**Foreign keys (CREATE TABLE constraints):**

```sql
FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE RESTRICT
```

**Additional constraint:** UNIQUE (student_id, week_start) — one progress record per student per week.

---

## Indexes

| Index name | Table | Columns | Reason |
|---|---|---|---|
| `idx_sessions_student` | sessions | student_id | filter/join by student |
| `idx_sessions_tutor` | sessions | tutor_id | utilization queries |
| `idx_sessions_subject` | sessions | subject_id | subject-level metrics |
| `idx_sessions_date` | sessions | session_date | week-range filters |
| `idx_progress_student` | student_progress | student_id | student lookup |
| `idx_progress_week` | student_progress | week_start | week-range filters |

---

## Referential integrity

SQLite foreign key enforcement is OFF by default. Every connection must run:

```sql
PRAGMA foreign_keys = ON;
```

---

## Target dataset (fake data)

| Entity | Count |
|---|---|
| subjects | 3 (Math, Computer Science, English) |
| tutors | 3 |
| students | 10 |
| sessions (target week) | 40 |
| student_progress rows | 10 |

Target week: **2024-01-15 to 2024-01-19** (Mon–Fri).
