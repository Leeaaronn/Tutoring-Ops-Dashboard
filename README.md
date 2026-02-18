# Tutoring Ops Dashboard

![CI](https://github.com/leeaa/Tutoring-Ops-Dashboard/actions/workflows/ci.yml/badge.svg)

Operational dashboard for tracking tutoring business metrics — sessions, revenue, student progress, and scheduling.

---

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
# Install dependencies
make install

# Run the dashboard
make run
```

## Development

```bash
make lint          # ruff lint check
make format        # auto-format with ruff
make format-check  # format check (CI mode)
make test          # run tests with coverage
make test-cov      # run tests + generate HTML coverage report
```

## Project Structure

```
src/dashboard/      # Streamlit app package
  app.py            # entry point
  pages/            # multi-page stubs
tests/              # pytest suite
```
