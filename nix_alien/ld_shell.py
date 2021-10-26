import argparse
import sys
from pathlib import Path
from string import Template

from .libs import get_unique_packages, find_libs
from .helpers import yes_or_no

SHELL_TEMPLATE = Template(
    """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) mkShell lib stdenv;
in
mkShell {
  name = "${name}-ld-shell";
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    ${packages}
  ];
  NIX_LD = lib.fileContents "$${stdenv.cc}/nix-support/dynamic-linker";
}
"""
)


def create_ld_shell(program: str) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path)

    return SHELL_TEMPLATE.substitute(
        name=path.name,
        packages=("\n" + 4 * " ").join(get_unique_packages(libs)),
    )


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument(
        "--destination",
        help="Where to create 'shell.nix' file",
        default="shell.nix",
    )
    parser.add_argument(
        "--yes",
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
        f.write(create_ld_shell(args.program))

    print(f"File '{args.destination}' created successfuly!")
