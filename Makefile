.PHONY: install lint format format-check test test-cov run

install:
	uv sync --all-extras

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

format-check:
	uv run ruff format --check src tests

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=html

run:
	uv run streamlit run src/dashboard/app.py
