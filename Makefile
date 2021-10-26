.PHONY = all ci format install test

all: install

install:
	poetry install

test:
	poetry run pytest -vv

ci:
	poetry run black --check .
	poetry run mypy . --ignore-missing-imports
	poetry run pytest -vv

format:
	poetry run black .
