import sys
import subprocess
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


def create_ld_shell(program_name: str) -> str:
    path = Path(program_name).expanduser()
    libs = find_libs(path)

    return SHELL_TEMPLATE.substitute(
        name=path.name, packages="\n    ".join(libs.values())
    )


def main(argv=sys.argv):
    program = argv[1]
    with open("shell.nix", "w") as f:
        f.write(create_ld_shell(program))

    subprocess.run(["nix-shell"])
