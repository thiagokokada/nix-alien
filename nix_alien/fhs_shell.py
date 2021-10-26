import argparse
import sys
from pathlib import Path
from string import Template

from .libs import get_unique_packages, find_libs
from .helpers import yes_or_no

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
        "--destination",
        help="Where to create 'default.nix' file",
        default="default.nix",
    )
    parser.add_argument(
        "--recreate",
        help="Ignore yes/no prompts",
        action="store_true",
    )

    args = parser.parse_args(args=args)

    if Path(args.destination).exists():
        if not args.yes and not yes_or_no(
            f"File '{args.destination}' already exist! Continue?"
        ):
            sys.exit(1)

    with open(args.destination, "w") as f:
        f.write(create_fhs_shell(args.program))

    print(f"File '{args.destination}' created successfuly!")
