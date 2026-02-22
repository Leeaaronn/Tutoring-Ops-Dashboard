Tutoring Ops Dashboard

A full-stack operational analytics system for a private tutoring business.

This project models a tutoring operation as a relational data system, computes weekly business KPIs via SQL, and exposes them through a lightweight Streamlit dashboard.

It is intentionally designed with strong data integrity guarantees, clean separation of concerns, and reproducible datasets.

Overview

The system answers four core operational questions:

What is the attendance rate this week?

What is the no-show rate by subject?

Are we over or under staffed (tutor utilization)?

Which students are at risk due to low progress?

The architecture separates:

Data generation

Storage layer (SQLite warehouse)

Metric computation layer (pure SQL)

Presentation layer (Streamlit UI)

Architecture
generate_fake_data.py
        ↓
CSV files (data/)
        ↓
load_sqlite.py → warehouse.db
        ↓
metrics.py (SQL metric layer)
        ↓
app.py (Streamlit UI)
Design Principles

Deterministic dataset for reproducible metric validation

Relational integrity enforced at the database level

Pure SQL metric layer (no ORM, no pandas)

Clear separation between storage, logic, and presentation

Minimal abstractions; explicit over clever

Data Model

Normalized schema with five tables:

subjects

tutors

students

sessions

student_progress

Integrity Guarantees

Primary keys on all entities

Foreign keys with ON DELETE RESTRICT

CHECK constraints for:

valid status values

positive scheduled hours

bounded progress percentage (0–100)

UNIQUE(student_id, week_start) for progress records

Indexed columns for metric queries

Foreign key enforcement is explicitly enabled on every connection.

Metric Layer

All KPIs are computed directly in SQL via parameterized queries:

Average weekly attendance rate

Subject-level no-show rate

Tutor utilization (booked_hours / available_hours)

At-risk students (progress_percent < 60)

Metrics operate over a weekly time window defined as:

session_date >= week_start
AND session_date < week_start + 7 days

This ensures deterministic, testable weekly aggregation.

Dashboard

The Streamlit UI surfaces:

Avg Attendance Rate

Computer Science No-Show Rate

Tutors >85% Utilization

At-Risk Student Count

Utilization breakdown

At-risk student list

Example week (2024-01-15):

Attendance: 85%

CS No-Show: 10%

High Utilization Tutors: 2

At-Risk Students: 2

Tech Stack

Python

SQLite

Streamlit

Ruff (linting & formatting)

Pytest

UV (dependency management)

No ORMs. No heavy frameworks.
The focus is correctness, clarity, and layered design.

Running Locally

From repository root:

uv sync
uv run python -m dashboard.data.load_sqlite
uv run streamlit run src/dashboard/app.py
Engineering Notes

Database is rebuilt idempotently on load.

CSV imports include explicit type coercion.

All SQL is parameterized.

No silent failure paths — missing database surfaces actionable errors.

Linting and formatting enforced via Ruff.

Future Enhancements

Multi-week trend analysis

Subject drilldowns

Deployment (Streamlit Cloud)

Role-based views

API layer for external consumers

Why This Project Matters

Operational analytics systems are often built incrementally and inconsistently.

This project demonstrates:

Thoughtful schema design

Data integrity enforcement

Deterministic metric validation

Clean service-layer boundaries

Full-stack data application architecture

It reflects how production analytics tooling should be structured — even at small scale.