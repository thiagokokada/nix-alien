PYTHON_RUN := python -m
.PHONY = all ci format install test

all: test

test:
	${PYTHON_RUN} pytest -vvv

ci:
	${PYTHON_RUN} black --check .
	${PYTHON_RUN} mypy --ignore-missing-imports .
	${PYTHON_RUN} pytest -vvv
	find -name '*.nix' -exec nixpkgs-fmt --check {} \+
	nix --experimental-features 'nix-command flakes' flake check

format:
	${PYTHON_RUN} black .
	find -name '*.nix' -exec nixpkgs-fmt {} \+
