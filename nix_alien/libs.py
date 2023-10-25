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
            "--top-level",
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
        if not dep.soname or dep.found:
            continue

        dep_candidates = find_lib_candidates(dep.soname)
        selected_dep = None

        if len(dep_candidates) == 0:
            _print(f"No candidate found for '{dep.soname}'", file=sys.stderr)
        elif len(dep_candidates) == 1:
            selected_dep = dep_candidates[0]
        else:
            if select_candidates:
                # Prioritise user selected candidates
                selected_dep = next(
                    (c for c in dep_candidates if re.search(select_candidates, c)), None
                )

            # Try to find an dependency that is already solved
            if not selected_dep:
                selected_dep = next(
                    (d for d in resolved_deps.values() if d in dep_candidates), None
                )

                # Show FZF to allow user to select the best dependency
                if not selected_dep:
                    fzf_options = join(
                        [
                            "--cycle",
                            "--prompt",
                            f"Select candidate for '{dep.soname}'> ",
                        ]
                    )
                    selected_dep = fzf.prompt(dep_candidates, fzf_options)[0]

        _print(
            f"Selected candidate for '{dep.soname}': {selected_dep}",
            file=sys.stderr,
        )
        resolved_deps[dep.soname] = selected_dep

    return resolved_deps


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
