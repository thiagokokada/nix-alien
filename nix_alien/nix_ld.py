from importlib.resources import read_text
from pathlib import Path
from string import Template
from typing import Iterable, Optional

from . import _impl

TEMPLATE = Template(read_text(__package__, "nix_ld.template.nix"))
FLAKE_TEMPLATE = Template(read_text(__package__, "nix_ld_flake.template.nix"))
MODULE = "nix-ld"


def create_nix_ld_drv(
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> str:
    return _impl.create_template_drv(
        template=TEMPLATE,
        program=program,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
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
    return _impl.create(
        template=TEMPLATE,
        module=MODULE,
        process_name=Path(program).name,
        program=program,
        args=args,
        destination=destination,
        recreate=recreate,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
    )


def create_nix_ld_drv_flake(
    program: str,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
) -> str:
    return _impl.create_template_drv_flake(
        template=FLAKE_TEMPLATE,
        program=program,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
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
    return _impl.create_flake(
        template=FLAKE_TEMPLATE,
        module=MODULE,
        program=program,
        args=args,
        destination=destination,
        recreate=recreate,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
    )


def main(args=None):
    return _impl.main(
        module=MODULE,
        create_fn=create_nix_ld,
        create_flake_fn=create_nix_ld_flake,
        args=args,
    )
