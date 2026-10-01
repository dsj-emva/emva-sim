.PHONY: install test lint generate

install:
	uv sync --locked

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

generate:
	uv run emva-sim generate --profile profiles/planned-hospitality.toml --setting middle --seed 1 --out out/
