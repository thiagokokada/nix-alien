import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from shlex import join
from typing import Optional, Union

from lddwrap import Dependency, list_dependencies
from pyfzf.pyfzf import FzfPrompt

from ._version import __version__
from .helpers import get_print

fzf = FzfPrompt()


def find_lib_candidates(basename: str) -> list[str]:
    result = subprocess.run(
        [
            "nix-locate",
            "--minimal",
            "--at-root",
            "--whole-name",
            os.path.join("/lib", basename),
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    candidates = result.stdout.strip().split("\n")
    return [c for c in candidates if c]


def find_libs(
    path: Union[Path, str],
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    select_candidates: Optional[str] = None,
) -> dict[str, Optional[str]]:
    _print = get_print(silent)
    path = Path(path).expanduser()
    deps = list_dependencies(path=path)

    for additional_lib in additional_libs:
        dep = Dependency(soname=additional_lib, found=False)
        deps.append(dep)

    resolved_deps: dict[str, Optional[str]] = {}

    for dep in deps:
        if not dep.soname or dep.found or dep.soname in resolved_deps:
            continue

        candidates = find_lib_candidates(dep.soname)
        selected_dep = select_dep_from_candidates(
            dep.soname, resolved_deps, candidates, select_candidates
        )

        if selected_dep is None:
            _print(f"No candidate found for '{dep.soname}'", file=sys.stderr)
        else:
            _print(
                f"Selected candidate for '{dep.soname}': {selected_dep}",
                file=sys.stderr,
            )

        resolved_deps[dep.soname] = selected_dep

    return resolved_deps


def select_dep_from_candidates(
    soname: str,
    resolved_deps: dict[str, Optional[str]],
    candidates: list[str],
    select_candidates: Optional[str] = None,
) -> Optional[str]:
    # Trivial cases
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Prioritise user selected candidates via --select-candidates flag
    if select_candidates and (
        selected_candidate := next(
            (c for c in candidates if re.search(select_candidates, c)), None
        )
    ):
        return selected_candidate

    # Try to find one match between the already resolved dependencies
    if resolved_candidate := next(
        (d for d in resolved_deps.values() if d in candidates), None
    ):
        return resolved_candidate

    # Show FZF to allow user to select the best dependency
    fzf_options = join(
        [
            "--cycle",
            "--prompt",
            f"Select candidate for '{soname}'> ",
        ]
    )
    return fzf.prompt(candidates, fzf_options)[0]


def get_unique_packages(libs: dict[str, Optional[str]]) -> Iterable[str]:
    # remove None values
    unique_packages = {lib for lib in libs.values() if lib is not None}
    return sorted(unique_packages)


def main(args=None):
    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to analyze")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-l",
        "--additional-libs",
        metavar="LIBRARY",
        help="Additional libraries to search. May be passed multiple times",
        action="append",
        default=[],
    )
    parser.add_argument(
        "-c",
        "--select-candidates",
        metavar="CANDIDATE",
        help=" ".join(
            [
                "Library candidates that will be auto-selected if found via regex.",
                "Useful for automation.",
            ]
        ),
        action="store",
    )
    parser.add_argument("-j", "--json", help="Output as json", action="store_true")
    parser.add_argument(
        "-s",
        "--silent",
        help="Silence informational messages",
        action="store_true",
    )

    parsed_args = parser.parse_args(args=args)
    libs = find_libs(
        parsed_args.program,
        silent=parsed_args.silent,
        additional_libs=parsed_args.additional_libs,
        select_candidates=parsed_args.select_candidates,
    )

    if parsed_args.json:
        print(json.dumps(libs, indent=2))
    else:
        print(" ".join(get_unique_packages(libs)))
