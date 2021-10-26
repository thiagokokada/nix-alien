import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Union

import lddwrap
from pyfzf.pyfzf import FzfPrompt

fzf = FzfPrompt()


def find_lib_candidates(basename: str):
    return (
        subprocess.run(
            ["nix-locate", "--minimal", "--whole-name", "--top-level", basename],
            check=True,
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split("\n")
    )


def find_libs(path: Union[Path, str]) -> Dict[str, Optional[str]]:
    path = Path(path).expanduser()
    deps = lddwrap.list_dependencies(path=path)
    resolved_deps = {}

    for dep in deps:
        if dep.found:
            continue

        candidates = find_lib_candidates(dep.soname)
        if len(candidates) == 0:
            print(f"No candidate found for '{dep.soname}'", file=sys.stderr)
            selected_candidate = None
        elif len(candidates) == 1:
            selected_candidate = candidates[0]
        else:
            intersection = set(resolved_deps.values()).intersection(candidates)
            if intersection:
                # Can be any candidate really, lets pick the first one
                selected_candidate = intersection.pop()
            else:
                selected_candidate = fzf.prompt(
                    candidates, f"--cycle --prompt '{dep.soname}> '"
                )[0]

        print(
            f"Selected candidate for '{dep.soname}': {selected_candidate}",
            file=sys.stderr,
        )
        resolved_deps[dep.soname] = selected_candidate

    return resolved_deps


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to analyze")

    args = parser.parse_args(args=args)
    libs = find_libs(args.program)
    print(" ".join([l for l in libs.values() if l]))  # remove None values
