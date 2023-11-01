import argparse
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from platform import machine
from typing import Callable, Optional

from ._version import version
from .helpers import edit_file, get_dest_path, get_print, read_template
from .libs import find_libs, get_unique_packages

REMOVE_WHITESPACES = re.compile(r"\s+")


def create_template_drv(
    template: str,
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
    _indent: int = 4,
) -> str:
    path = Path(program).expanduser()
    packages = find_libs(path, silent, additional_libs, select_candidates)

    return read_template(template).safe_substitute(
        __name__=REMOVE_WHITESPACES.sub("_", path.name),
        __packages__=("\n" + _indent * " ").join(
            list(get_unique_packages(packages)) + list(additional_packages)
        ),
        __program__=shlex.quote(str(path.absolute())),
    )


def create(
    template: str,
    process_name: str,
    program: str,
    args: Iterable[str],
    destination: Path,
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
) -> None:
    if recreate:
        destination.unlink(missing_ok=True)

    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        fhs_shell = create_template_drv(
            template,
            program,
            silent,
            additional_libs,
            additional_packages,
            select_candidates,
        )
        with open(destination, "w", encoding="locale") as file:
            file.write(fhs_shell)
        get_print(silent)(f"File '{destination}' created successfuly!", file=sys.stderr)

    build_path = Path(
        subprocess.run(
            ["nix-build", "--no-out-link", destination],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
    )

    sys.stderr.flush()
    sys.stdout.flush()
    os.execv(
        build_path / "bin" / REMOVE_WHITESPACES.sub("_", process_name),
        [process_name, *args],
    )


def create_template_drv_flake(
    template: str,
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
    _indent: int = 12,
) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path, silent, additional_libs, select_candidates)

    return read_template(template).safe_substitute(
        __name__=path.name,
        __packages__=("\n" + _indent * " ").join(
            list(get_unique_packages(libs)) + list(additional_packages)
        ),
        __program__=path.absolute(),
        __system__=f"{machine()}-linux",
    )


def create_flake(
    template: str,
    program: str,
    args: Iterable[str],
    destination: Path,
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
) -> None:
    if recreate:
        destination.unlink(missing_ok=True)

    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        fhs_shell = create_template_drv_flake(
            template,
            program,
            silent,
            additional_libs,
            additional_packages,
            select_candidates,
        )
        with open(destination, "w", encoding="locale") as file:
            file.write(fhs_shell)
        get_print(silent)(f"File '{destination}' created successfuly!", file=sys.stderr)

    sys.stderr.flush()
    sys.stdout.flush()
    os.execvp(
        "nix",
        [
            "nix",
            "run",
            "--experimental-features",
            "nix-command flakes",
            str(destination.parent),
            "--",
            *args,
        ],
    )


def main(
    module: str,
    create_fn: Callable,
    create_flake_fn: Callable,
    args: Optional[list] = None,
) -> None:
    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Program to run")
    parser.add_argument("--version", action="version", version=version)
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
        "-c",
        "--select-candidates",
        metavar="CANDIDATE",
        help=" ".join(
            [
                "Library candidates that will be auto-selected if found via regex.",
                "Useful for automation.",
            ]
        ),
        action="store",
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
        "-E",
        "--edit",
        help="Edit 'default.nix' using $EDITOR (or 'nano' if unset)",
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

    if parsed_args.flake:
        filename = "flake.nix"
    else:
        filename = "default.nix"

    destination = get_dest_path(
        parsed_args.destination,
        parsed_args.program,
        module,
        filename,
    )

    if parsed_args.print_destination:
        print(destination)
    elif parsed_args.edit:
        edit_file(destination)
    elif parsed_args.flake:
        create_flake_fn(
            program=parsed_args.program,
            args=parsed_args.ellipsis,
            destination=destination,
            recreate=parsed_args.recreate,
            additional_libs=parsed_args.additional_libs,
            additional_packages=parsed_args.additional_packages,
            select_candidates=parsed_args.select_candidates,
            silent=parsed_args.silent,
        )
    else:
        create_fn(
            program=parsed_args.program,
            args=parsed_args.ellipsis,
            destination=destination,
            recreate=parsed_args.recreate,
            additional_libs=parsed_args.additional_libs,
            additional_packages=parsed_args.additional_packages,
            select_candidates=parsed_args.select_candidates,
            silent=parsed_args.silent,
        )
