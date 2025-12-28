.PHONY: deploy test lint format clean install

deploy:
	uv run qgis-manage deploy

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff check --fix .

clean:
	uv run qgis-manage clean

install:
	uv run pre-commit install
