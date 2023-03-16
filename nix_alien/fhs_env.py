from pathlib import Path
from typing import Iterable, Optional

from . import _impl

TEMPLATE = "fhs_env.template.nix"
FLAKE_TEMPLATE = "fhs_env_flake.template.nix"
MODULE = "fhs-env"


def create_fhs_env_drv(
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


def create_fhs_env(
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
        process_name=f"{Path(program).name}-fhs",
        program=program,
        args=args,
        destination=destination,
        recreate=recreate,
        silent=silent,
        additional_libs=additional_libs,
        additional_packages=additional_packages,
    )


def create_fhs_env_drv_flake(
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


def create_fhs_env_flake(
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
        create_fn=create_fhs_env,
        create_flake_fn=create_fhs_env_flake,
        args=args,
    )
