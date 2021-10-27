PYTHON_RUN := python -m
.PHONY = all ci format install test

all: test

test:
	${PYTHON_RUN} pytest -vvv

ci:
	${PYTHON_RUN} black --check .
	${PYTHON_RUN} mypy --ignore-missing-imports .
    # FIXME: seems like hashlib/UUID depends on host or something
	${PYTHON_RUN} pytest -vvv --ignore=tests/test_helpers.py
	find -name '*.nix' -exec nixpkgs-fmt --check {} \+
	nix --experimental-features 'nix-command flakes' flake check

format:
	${PYTHON_RUN} black .
	find -name '*.nix' -exec nixpkgs-fmt {} \+
