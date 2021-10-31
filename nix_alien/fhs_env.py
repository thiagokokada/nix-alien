import argparse
import subprocess
import sys
from importlib.resources import read_text
from pathlib import Path
from platform import machine
from string import Template
from typing import Iterable, Optional

from .libs import get_unique_packages, find_libs
from .helpers import get_dest_path, get_print

FHS_TEMPLATE = Template(read_text(__package__, "fhs_env.template.nix"))
FHS_FLAKE_TEMPLATE = Template(read_text(__package__, "fhs_env_flake.template.nix"))


def create_fhs_env_drv(program: str, silent: bool = False) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path, silent)

    return FHS_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 4 * " ").join(get_unique_packages(libs)),
        __program__=path.absolute(),
    )


def create_fhs_env(
    program: str,
    args: Iterable[str],
    destination: Optional[str],
    recreate: bool = False,
    silent: bool = False,
) -> None:
    dest_path = get_dest_path(destination, program, "fhs-env", "default.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        fhs_shell = create_fhs_env_drv(program, silent)
        with open(dest_path, "w") as f:
            f.write(fhs_shell)
        get_print(silent)(f"File '{dest_path}' created successfuly!", file=sys.stderr)

    build_path = Path(
        subprocess.run(
            ["nix-build", "--no-out-link", dest_path],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    name = Path(program).name
    subprocess.run([build_path / "bin" / f"{name}-fhs", *args])


def create_fhs_env_drv_flake(program: str, silent: bool = False) -> str:
    path = Path(program).expanduser()
    libs = find_libs(path, silent)

    return FHS_FLAKE_TEMPLATE.safe_substitute(
        __name__=path.name,
        __packages__=("\n" + 12 * " ").join(get_unique_packages(libs)),
        __program__=path.absolute(),
        __system__=f"{machine()}-linux",
    )


def create_fhs_env_flake(
    program: str,
    args: Iterable[str],
    destination: Optional[str],
    recreate: bool = False,
    silent: bool = False,
) -> None:
    dest_path = get_dest_path(destination, program, "fhs-env", "flake.nix")

    if recreate:
        dest_path.unlink(missing_ok=True)

    if not dest_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        fhs_shell = create_fhs_env_drv_flake(program, silent)
        with open(dest_path, "w") as f:
            f.write(fhs_shell)
        get_print(silent)(f"File '{dest_path}' created successfuly!", file=sys.stderr)

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
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to be passed to the program",
    )
    parsed_args = parser.parse_args(args=args)

    if parsed_args.flake:
        create_fhs_env_flake(
            program=parsed_args.program,
            args=parsed_args.args,
            destination=parsed_args.destination,
            recreate=parsed_args.recreate,
            silent=parsed_args.silent,
        )
    else:
        create_fhs_env(
            program=parsed_args.program,
            args=parsed_args.args,
            destination=parsed_args.destination,
            recreate=parsed_args.recreate,
            silent=parsed_args.silent,
        )
