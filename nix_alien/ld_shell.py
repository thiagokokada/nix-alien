import argparse
import sys
from pathlib import Path
from string import Template

from .libs import find_libs

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
    # Remove None values
    unique_packages = set([l for l in libs.values() if l])

    return SHELL_TEMPLATE.substitute(
        name=path.name,
        packages=("\n" + 4 * " ").join(sorted(unique_packages)),
    )


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument(
        "--destination",
        help="Where to create 'shell.nix' file",
        default="shell.nix",
    )

    args = parser.parse_args(args=args)
    with open(args.destination, "w") as f:
        f.write(create_ld_shell(args.program))
