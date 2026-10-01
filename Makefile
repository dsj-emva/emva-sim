.PHONY: install test lint

install:
	uv sync --locked

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
