.PHONY: deploy test lint format clean install help

deploy:
	uv run qgis-manage deploy

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff check --fix .
	uv run ruff format .

clean:
	uv run qgis-manage clean

install:
	uv run pre-commit install

help:
	uv run python scripts/generate_help.py
