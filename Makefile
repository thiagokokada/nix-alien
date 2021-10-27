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
	find -name '*.nix' -exec nixpkgs-fmt {} --check \+

format:
	poetry run black .
	find -name '*.nix' -exec nixpkgs-fmt {} \+
