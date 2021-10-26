import subprocess
from pathlib import Path
from typing import Dict, Optional

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


def find_libs(path: Path) -> Dict[str, Optional[str]]:
    deps = lddwrap.list_dependencies(path=path)
    resolved_deps = {}

    for dep in deps:
        if dep.found:
            continue

        candidates = find_lib_candidates(dep.soname)
        if len(candidates) == 0:
            print(f"No candidate found for '{dep.soname}'")
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

        print(f"Selected candidate for '{dep.soname}': {selected_candidate}")
        resolved_deps[dep.soname] = selected_candidate

    return resolved_deps
