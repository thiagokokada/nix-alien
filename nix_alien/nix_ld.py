import argparse
import subprocess
import sys
from importlib.resources import read_text
from pathlib import Path
from platform import machine
from string import Template
from typing import Optional

from .libs import get_unique_packages, find_libs
from .helpers import get_dest_path

NIX_LD_TEMPLATE = Template(read_text(__package__, "nix_ld.template.nix"))
NIX_LD_FLAKE_TEMPLATE = Template(read_text(__package__, "nix_ld_flake.template.nix"))


def create_nix_ld_drv(program: str) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path)

    return NIX_LD_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 4 * " ").join(get_unique_packages(libs)),
        __program__=path.absolute(),
    )


def create_nix_ld(
    program: str,
    args: list[str],
    destination: Optional[str],
    recreate: bool = False,
) -> None:
    dest_path = get_dest_path(destination, program, "nix-ld", "default.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        ld_shell = create_nix_ld_drv(program)
        with open(dest_path, "w") as f:
            f.write(ld_shell)
        print(f"File '{dest_path}' created successfuly!")

    build_path = Path(
        subprocess.run(
            ["nix-build", "--no-out-link", dest_path],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    name = Path(program).name
    subprocess.run([build_path / "bin" / name, *args])


def create_nix_ld_drv_flake(program: str) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path)

    return NIX_LD_FLAKE_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 12 * " ").join(get_unique_packages(libs)),
        __program__=path.absolute(),
        __system__=f"{machine()}-linux",
    )


def create_nix_ld_flake(
    program: str,
    args: list[str],
    destination: Optional[str],
    recreate: bool = False,
) -> None:
    dest_path = get_dest_path(destination, program, "nix-ld", "flake.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        ld_shell = create_nix_ld_drv_flake(program)
        with open(dest_path, "w") as f:
            f.write(ld_shell)
        print(f"File '{dest_path}' created successfuly!")

    subprocess.run(
        [
            "nix",
            "run",
            "--experimental-features",
            "nix-command flakes",
            dest_path.parent,
            "--",
            *args,
        ]
    )


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument(
        "-r",
        "--recreate",
        help="Recreate 'default.nix' file if exists",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--destination",
        metavar="PATH",
        help="Path where 'default.nix' file will be created",
    )
    parser.add_argument(
        "-f",
        "--flake",
        help="Create and use 'flake.nix' file instead (experimental)",
        action="store_true",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to be passed to the program",
    )
    parsed_args = parser.parse_args(args=args)

    if parsed_args.flake:
        create_nix_ld_flake(
            program=parsed_args.program,
            args=parsed_args.args,
            destination=parsed_args.destination,
            recreate=parsed_args.recreate,
        )
    else:
        create_nix_ld(
            program=parsed_args.program,
            args=parsed_args.args,
            destination=parsed_args.destination,
            recreate=parsed_args.recreate,
        )
