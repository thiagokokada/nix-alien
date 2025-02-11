from collections.abc import Iterable
from pathlib import Path
from typing import Optional

from . import _impl

TEMPLATE = "nix_ld.template.nix"
FLAKE_TEMPLATE = "nix_ld_flake.template.nix"
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
    destination: Path,
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
) -> None:
    return _impl.create(
        template=TEMPLATE,
        process_name=Path(program).name,
        program=program,
        args=args,
        destination=destination,
        recreate=recreate,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
        select_candidates=select_candidates,
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
    destination: Path,
    recreate: bool = False,
    silent: bool = False,
    additional_libs: Iterable[str] = (),
    additional_packages: Iterable[str] = (),
    select_candidates: Optional[str] = None,
) -> None:
    return _impl.create_flake(
        template=FLAKE_TEMPLATE,
        program=program,
        args=args,
        destination=destination,
        recreate=recreate,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
        select_candidates=select_candidates,
    )


def main(args=None):
    return _impl.main(
        module=MODULE,
        create_fn=create_nix_ld,
        create_flake_fn=create_nix_ld_flake,
        args=args,
    )
