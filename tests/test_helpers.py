from uuid import UUID
from pathlib import Path

from nix_alien import helpers


def test_get_hash_for_program():
    assert helpers.get_hash_for_program("/abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
    assert helpers.get_hash_for_program("/./abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
    assert helpers.get_hash_for_program("/xyz/../abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
    assert helpers.get_hash_for_program("/foo/bar") == UUID(
        "aca1aca4-b9b7-5083-839b-120863df4c7d"
    )


def test_get_cache_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_cache_path("/abc") == Path(
        "/home/nameless-shelter/.cache/nix-alien/f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_cache_path("/abc") == Path(
        "/nix-alien/f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
