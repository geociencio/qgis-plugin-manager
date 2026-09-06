.PHONY: deploy test lint format clean install help

deploy:
	uv run qgis-manage deploy

test:
	uv run python -m unittest discover tests

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff check --fix .

clean:
	uv run qgis-manage clean

install:
	uv run pre-commit install

help:
	uv run python scripts/generate_help.py
