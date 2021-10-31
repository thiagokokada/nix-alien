import os
from typing import Optional
import uuid
from pathlib import Path

UUID_NAMESPACE = uuid.UUID("f318d4a6-dd46-47ce-995d-e95c17cadcc0")


def get_hash_for_program(program: str) -> uuid.UUID:
    path = Path(program).expanduser().absolute().resolve()
    return uuid.uuid5(UUID_NAMESPACE, str(path))


def get_cache_path(program: str) -> Path:
    xdg_cache_home = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser()
    return xdg_cache_home / "nix-alien" / str(get_hash_for_program(program))


def get_dest_path(
    destination: Optional[str],
    program: str,
    directory: str,
    filename: str,
) -> Path:
    if destination:
        return Path(destination).expanduser().resolve() / filename
    else:
        return get_cache_path(program) / directory / filename
