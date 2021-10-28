#!/usr/bin/env nix-shell
#!nix-shell shell.nix -i "make -f"

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
	NIXPKGS_ALLOW_UNSUPPORTED_SYSTEM=1 nix --experimental-features 'nix-command flakes' flake check --impure

format:
	${PYTHON_RUN} black .
	find -name '*.nix' -exec nixpkgs-fmt {} \+
