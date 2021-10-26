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


def create_ld_shell(program: str) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path)

    return SHELL_TEMPLATE.substitute(
        name=path.name,
        packages=("\n" + 4 * " ").join(
            [l for l in libs.values() if l]
        ),  # remove None values
    )


def main(argv=sys.argv):
    program = argv[1]
    with open("shell.nix", "w") as f:
        f.write(create_ld_shell(program))

    subprocess.run(["nix-shell"])
