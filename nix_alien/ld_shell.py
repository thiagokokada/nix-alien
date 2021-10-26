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

    args = parser.parse_args(args=args)
    cache_file = get_cache_path(args.program) / "shell.nix"

    if args.recreate:
        cache_file.unlink(missing_ok=True)

    if not cache_file.exists():
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            f.write(create_ld_shell(args.program))
        print(f"File '{cache_file}' created successfuly!")

    subprocess.run(["nix-shell", str(cache_file)])
