import argparse
import os
import subprocess
import sys
from importlib.resources import read_text
from pathlib import Path
from platform import machine
from string import Template
from typing import Iterable, Optional

from ._version import __version__
from .libs import get_unique_packages, find_libs
from .helpers import get_dest_path, get_print

NIX_LD_TEMPLATE = Template(read_text(__package__, "nix_ld.template.nix"))
NIX_LD_FLAKE_TEMPLATE = Template(read_text(__package__, "nix_ld_flake.template.nix"))
MODULE = "nix-ld"


def create_nix_ld_drv(
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> str:
    path = Path(program).expanduser()
    packages = find_libs(path, silent, additional_libs)

    return NIX_LD_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 4 * " ").join(
            list(get_unique_packages(packages)) + list(additional_packages)
        ),
        __program__=path.absolute(),
    )


def create_nix_ld(
    program: str,
    args: Iterable[str],
    destination: Optional[str],
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> None:
    dest_path = get_dest_path(destination, program, MODULE, "default.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        ld_shell = create_nix_ld_drv(
            program, silent, additional_libs, additional_packages
        )
        with open(dest_path, "w", encoding="locale") as file:
            file.write(ld_shell)
        get_print(silent)(f"File '{dest_path}' created successfuly!", file=sys.stderr)

    build_path = Path(
        subprocess.run(
            ["nix-build", "--no-out-link", dest_path],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
    )

    process_name = Path(program).name

    sys.stderr.flush()
    sys.stdout.flush()
    os.execv(build_path / "bin" / process_name, [process_name, *args])


def create_nix_ld_drv_flake(
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path, silent, additional_libs)

    return NIX_LD_FLAKE_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 12 * " ").join(
            list(get_unique_packages(libs)) + list(additional_packages)
        ),
        __program__=path.absolute(),
        __system__=f"{machine()}-linux",
    )


def create_nix_ld_flake(
    program: str,
    args: Iterable[str],
    destination: Optional[str],
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> None:
    dest_path = get_dest_path(destination, program, MODULE, "flake.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        ld_shell = create_nix_ld_drv_flake(
            program, silent, additional_libs, additional_packages
        )
        with open(dest_path, "w", encoding="locale") as file:
            file.write(ld_shell)
        get_print(silent)(f"File '{dest_path}' created successfuly!", file=sys.stderr)

    sys.stderr.flush()
    sys.stdout.flush()
    os.execvp(
        "nix",
        [
            "nix",
            "run",
            "--experimental-features",
            "nix-command flakes",
            str(dest_path.parent),
            "--",
            *args,
        ],
    )


def main(args=None):
    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-l",
        "--additional-libs",
        metavar="LIBRARY",
        help="Additional library to search. May be passed multiple times",
        action="append",
        default=[],
    )
    parser.add_argument(
        "-p",
        "--additional-packages",
        metavar="PACKAGE",
        help="Additional package to add. May be passed multiple times",
        action="append",
        default=[],
    )
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
        "-P",
        "--print-destination",
        help="Print where 'default.nix' file is located and exit",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--silent",
        help="Silence informational messages",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--flake",
        help="Create and use 'flake.nix' file instead (experimental)",
        action="store_true",
    )
    # argparse.REMAINDER is represented as '...'
    parser.add_argument(
        "ellipsis",
        nargs=argparse.REMAINDER,
        help="Arguments to be passed to the program",
    )
    parsed_args = parser.parse_args(args=args)

    if parsed_args.print_destination:
        if parsed_args.flake:
            print(
                get_dest_path(
                    parsed_args.destination,
                    parsed_args.program,
                    MODULE,
                    "flake.nix",
                )
            )
        else:
            print(
                get_dest_path(
                    parsed_args.destination,
                    parsed_args.program,
                    MODULE,
                    "default.nix",
                )
            )
    else:
        if parsed_args.flake:
            create_nix_ld_flake(
                program=parsed_args.program,
                args=parsed_args.ellipsis,
                destination=parsed_args.destination,
                recreate=parsed_args.recreate,
                additional_libs=parsed_args.additional_libs,
                additional_packages=parsed_args.additional_packages,
                silent=parsed_args.silent,
            )
        else:
            create_nix_ld(
                program=parsed_args.program,
                args=parsed_args.ellipsis,
                destination=parsed_args.destination,
                recreate=parsed_args.recreate,
                additional_libs=parsed_args.additional_libs,
                additional_packages=parsed_args.additional_packages,
                silent=parsed_args.silent,
            )
