# Tutoring Ops Dashboard

[![CI](https://github.com/Leeaaronn/Tutoring-Ops-Dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Leeaaronn/Tutoring-Ops-Dashboard/actions/workflows/ci.yml)

Operational analytics dashboard for tutoring businesses.
Built with Python, SQLite, and Streamlit. Implements a normalized relational schema, SQL-based metric layer, and an interactive UI for weekly operational insights.

I built this because I tutor CS to middle school students and saw how much operational data gets lost when everything runs on paper and whiteboards. This project models what a small tutoring center's data infrastructure *should* look like.

## Live Demo

👉 **[tutoring-ops-dashboard.streamlit.app](https://tutoring-ops-dashboard-egxejskngaonj77rlauyso.streamlit.app/)**

<img width="2481" height="945" alt="image" src="https://github.com/user-attachments/assets/95a82a04-3328-46c5-99e9-86cadb5a6bd7" />

---

## Problem

Tutoring operations require answering questions like:

- What is this week's attendance rate?
- Which subjects have high no-show rates?
- Are tutors over capacity?
- Which students are falling behind?

This project models those operational concerns end-to-end: data generation → schema design → SQL metrics → interactive dashboard.

---

## Architecture

```
data/*.csv → SQLite warehouse → metrics.py (SQL layer) → Streamlit UI
```

### Data Layer
- SQLite database (`warehouse.db`)
- Normalized schema with:
  - Foreign key constraints
  - CHECK constraints
  - Composite UNIQUE constraints
  - Indexed query paths

### Metric Layer
Pure SQL aggregation functions:
- `avg_attendance_rate`
- `no_show_rate`
- `tutor_utilization`
- `at_risk_students`

All metrics accept a `sqlite3.Connection` and week parameter.

### UI Layer
Streamlit dashboard featuring:
- Dynamic week selector (populated from DB)
- Subject filter for no-show rate
- Capacity warning banner
- Utilization progress bars
- Trend visualization
- At-risk student table

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud) with automatic redeploys on push to `main`.

---

## Key Design Decisions

- `src/` layout for clean packaging
- Pure SQL metrics instead of pandas-heavy logic
- Foreign key enforcement (`PRAGMA` ON)
- Ruff lint + format
- Pytest + coverage
- Deterministic fake data generation

---

## Local Development

```bash
# Install dependencies
uv sync

# Generate database
uv run python -m dashboard.data.load_sqlite

# Run dashboard
uv run streamlit run src/dashboard/app.py
```

## Testing & Linting

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

---

## Tech Stack

| Tool | Role |
|------|------|
| Python | Core language |
| SQLite | Data warehouse |
| Streamlit | Dashboard UI + Cloud deployment |
| Ruff | Linting & formatting |
| Pytest | Testing with coverage |
| UV | Dependency management |
| GitHub Actions | CI pipeline |

---

## Future Improvements

- Multi-week trend analysis
- Role-based views (manager vs tutor)
- Deployment to containerized environment
- Replace SQLite with Postgres backend

### Research Extensions

- Forecast tutor utilization via time-series modeling
- Predict at-risk students using classification
- Optimize scheduling as a constraint problem

---

## Why This Project

Operational analytics at small businesses is usually an afterthought — scattered spreadsheets, manual headcounts, gut-feel decisions. This project demonstrates that even at small scale, you can build a system with thoughtful schema design, enforced data integrity, deterministic metrics, and clean architecture. It reflects how production analytics tooling should be structured.