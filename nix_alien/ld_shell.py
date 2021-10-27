import argparse
import subprocess
import sys
from pathlib import Path
from string import Template

from .libs import get_unique_packages, find_libs
from .helpers import get_cache_path

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
        "--recreate",
        help="Recreate 'shell.nix' file if exists",
        action="store_true",
    )
    parser.add_argument(
        "--destination",
        metavar="PATH",
        help="Path where 'shell.nix' file will be created",
    )

    parsed_args = parser.parse_args(args=args)
    if parsed_args.destination:
        destination = Path(parsed_args.destination).expanduser().resolve() / "shell.nix"
    else:
        destination = get_cache_path(parsed_args.program) / "shell.nix"

    if parsed_args.recreate:
        destination.unlink(missing_ok=True)

    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w") as f:
            f.write(create_ld_shell(parsed_args.program))
        print(f"File '{destination}' created successfuly!")

    subprocess.run(["nix-shell", str(destination)])
