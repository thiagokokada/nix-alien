import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

import lddwrap
from fzf import fzf

from .helpers import get_print


def find_lib_candidates(basename: str) -> list[str]:
    result = subprocess.run(
        ["nix-locate", "--minimal", "--whole-name", "--top-level", basename],
        check=True,
        capture_output=True,
        text=True,
    )
    candidates = result.stdout.strip().split("\n")
    return [c for c in candidates if c != ""]


def find_libs(path: Union[Path, str], silent: bool = False) -> dict[str, Optional[str]]:
    _print = get_print(silent)
    path = Path(path).expanduser()
    deps = lddwrap.list_dependencies(path=path)
    resolved_deps: dict[str, Optional[str]] = {}

    for dep in deps:
        if not dep.soname or dep.found:
            continue

        candidates = find_lib_candidates(dep.soname)
        if len(candidates) == 0:
            _print(f"No candidate found for '{dep.soname}'", file=sys.stderr)
            selected_candidate = None
        elif len(candidates) == 1:
            selected_candidate = candidates[0]
        else:
            intersection = set(resolved_deps.values()).intersection(candidates)
            if intersection:
                # Can be any candidate really, lets pick the first one
                selected_candidate = intersection.pop()
            else:
                selected_candidate = fzf(
                    candidates,
                    cycle=True,
                    prompt=f"Select candidate for '${dep.soname}'> ",
                )[0].output

        _print(
            f"Selected candidate for '{dep.soname}': {selected_candidate}",
            file=sys.stderr,
        )
        resolved_deps[dep.soname] = selected_candidate

    return resolved_deps


def get_unique_packages(libs: dict[str, Optional[str]]) -> list[str]:
    # remove None values
    unique_packages = set([l for l in libs.values() if l])
    return sorted(unique_packages)


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to analyze")
    parser.add_argument("-j", "--json", help="Output as json", action="store_true")
    parser.add_argument(
        "-s",
        "--silent",
        help="Silence informational messages",
        action="store_true",
    )

    parsed_args = parser.parse_args(args=args)
    libs = find_libs(parsed_args.program, silent=parsed_args.silent)

    if parsed_args.json:
        print(json.dumps(libs, indent=2))
    else:
        print(" ".join(get_unique_packages(libs)))
