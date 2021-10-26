import argparse
import subprocess
import sys
from pathlib import Path
from string import Template

from .libs import get_unique_packages, find_libs
from .helpers import get_cache_path

FHS_TEMPLATE = Template(
    """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) buildFHSUserEnv;
in
buildFHSUserEnv {
  name = "${name}-fhs";
  targetPkgs = p: with p; [
    ${packages}
  ];
  runScript = "${program}";
}
"""
)


def create_fhs_shell(program: str) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path)

    return FHS_TEMPLATE.substitute(
        name=path.name,
        packages=("\n" + 4 * " ").join(get_unique_packages(libs)),
        program=path.absolute(),
    )


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument(
        "--recreate",
        help="Recreate 'default.nix' file if exists",
        action="store_true",
    )

    args = parser.parse_args(args=args)
    cache_file = get_cache_path(args.program) / "default.nix"
    name = Path(args.program).name

    if args.recreate:
        cache_file.unlink(missing_ok=True)

    if not cache_file.exists():
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            f.write(create_fhs_shell(args.program))
        print(f"File '{cache_file}' created successfuly!")

    build_path = Path(
        subprocess.run(
            ["nix-build", "--no-out-link", cache_file],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    subprocess.run([build_path / "bin" / f"{name}-fhs"])
