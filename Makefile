.PHONY: install test lint generate datasets vary-phrases

install:
	uv sync --locked

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

generate:
	uv run emva-sim generate --profile profiles/planned-hospitality.toml --setting middle --seed 1 --out out/

datasets:
	uv run emva-sim datasets --profile profiles/planned-hospitality.toml --out out/datasets

# Sends each phrase of the bank missing from the cache to Claude Haiku 4.5 once (needs
# ANTHROPIC_API_KEY in the environment or .env); commit the cache it writes.
vary-phrases:
	uv run emva-sim vary-phrases --profile profiles/planned-hospitality.toml
