# Tutoring Ops Dashboard

[![CI](https://github.com/Leeaaronn/Tutoring-Ops-Dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Leeaaronn/Tutoring-Ops-Dashboard/actions/workflows/ci.yml)

A full-stack operational analytics system for a private tutoring business. Built with SQLite, pure SQL metrics, and Streamlit — no ORMs, no heavy frameworks.

I built this because I tutor CS to middle school students and saw how much operational data gets lost when everything runs on paper and whiteboards. This project models what a small tutoring center's data infrastructure *should* look like.

<img width="2481" height="945" alt="image" src="https://github.com/user-attachments/assets/95a82a04-3328-46c5-99e9-86cadb5a6bd7" />

---

## What It Answers

- **What is the attendance rate this week?**
- **What is the no-show rate by subject?**
- **Are we over or under staffed?** (tutor utilization)
- **Which students are at risk?** (progress < 60%)

---

## Architecture

```
generate_fake_data.py → CSV files (data/)
                            ↓
                      load_sqlite.py → warehouse.db
                            ↓
                      metrics.py (pure SQL layer)
                            ↓
                      app.py (Streamlit UI)
```

Each layer has a single responsibility: generation, storage, computation, presentation.

---

## Data Model

Five normalized tables with full relational integrity:

| Table | Purpose |
|-------|---------|
| `subjects` | Subject catalog |
| `tutors` | Tutor roster with weekly available hours |
| `students` | Student enrollment linked to subjects |
| `sessions` | Individual session records with attendance status |
| `student_progress` | Weekly progress scores per student |

**Integrity enforced at the database level:** primary keys, foreign keys with `ON DELETE RESTRICT`, `CHECK` constraints on status values and bounded percentages, `UNIQUE` on progress records, and indexed columns for metric queries. Foreign key enforcement is explicitly enabled on every connection.

---

## Metrics

All KPIs are computed in pure SQL with parameterized queries over a rolling weekly window:

| Metric | Query Logic |
|--------|-------------|
| Attendance Rate | `attended / total sessions` within week |
| No-Show Rate | `no_show / total` grouped by subject |
| Tutor Utilization | `booked_hours / available_hours` per tutor |
| At-Risk Students | `progress_percent < 60` in current week |

**Example output (week of 2024-01-15):**

| KPI | Value |
|-----|-------|
| Attendance | 85% |
| CS No-Show Rate | 10% |
| High Utilization Tutors | 2 |
| At-Risk Students | 2 |

---

## Tech Stack

| Tool | Role |
|------|------|
| Python | Core language |
| SQLite | Data warehouse |
| Streamlit | Dashboard UI |
| Ruff | Linting & formatting |
| Pytest | Testing with coverage |
| UV | Dependency management |
| GitHub Actions | CI pipeline |

---

## Running Locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
uv run python -m dashboard.data.load_sqlite
uv run streamlit run src/dashboard/app.py
```

## Development

```bash
make lint          # ruff lint check
make format        # auto-format
make test          # run tests with coverage
make test-cov      # tests + HTML coverage report
```

---

## Design Decisions

- **Pure SQL over pandas** — metrics are testable, portable, and don't hide logic behind dataframe operations
- **Deterministic fake data** — seeded generation ensures reproducible metric validation across environments
- **Idempotent database loads** — warehouse rebuilds cleanly on every run
- **No silent failures** — missing database surfaces actionable errors, not empty dashboards
- **Parameterized queries throughout** — no string concatenation, no injection risk

---

## Future Work

- Multi-week trend analysis
- Subject-level drilldowns
- Deployment to Streamlit Cloud
- Role-based views (tutor vs. admin)
- API layer for external consumers

---

## Why This Project

Operational analytics at small businesses is usually an afterthought — scattered spreadsheets, manual headcounts, gut-feel decisions. This project demonstrates that even at small scale, you can build a system with thoughtful schema design, enforced data integrity, deterministic metrics, and clean architecture. It reflects how production analytics tooling should be structured.
