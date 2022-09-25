#!/usr/bin/env nix-shell
#!nix-shell shell.nix -i "make -f"

PYTHON_RUN := python -m
.PHONY = all ci format install test update

all: test

test:
	${PYTHON_RUN} pytest -vvv

ci:
	find -name '*.nix' -exec nixpkgs-fmt --check {} \+
	nix --experimental-features 'nix-command flakes' flake check

format:
	${PYTHON_RUN} black .
	find -name '*.nix' -exec nixpkgs-fmt {} \+

update:
	poetry update
	touch flake.nix
