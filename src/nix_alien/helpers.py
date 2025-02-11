import os
import subprocess
import uuid
from functools import partial
from importlib.resources import files
from pathlib import Path
from string import Template
from typing import Callable, Optional

UUID_NAMESPACE = uuid.UUID("eebf3397-2041-4370-bf33-937b33d5c959")


def edit_file(file: Path) -> subprocess.CompletedProcess:
    editor = os.environ.get("EDITOR", "nano")
    # Explicitly not checking the result here since it doesn't matter
    # if the editor exists successfully or not here
    return subprocess.run([editor, file], check=False)


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
    return get_cache_path(program) / directory / filename


def get_print(silent: bool = False) -> Callable[..., None]:
    if silent:
        return lambda *_, **__: None
    return partial(print, "[nix-alien]")


def read_template(filename: str) -> Template:
    return Template(files(__package__).joinpath(filename).read_text())
