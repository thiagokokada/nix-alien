from uuid import UUID
from pathlib import Path

from nix_alien import helpers


def test_get_hash_for_program():
    assert helpers.get_hash_for_program("abc") == UUID(
        "eceff178-9c32-5b49-95a8-497055982343"
    )
    assert helpers.get_hash_for_program("foo") == UUID(
        "1f32dd6c-279f-5ecb-a475-32cb677e9a9f"
    )
    assert helpers.get_hash_for_program("bar") == UUID(
        "bbca8297-c17d-5454-a75c-da3f77ac2303"
    )


def test_get_cache_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_cache_path("abc") == Path(
        "/home/nameless-shelter/.cache/nix-alien/eceff178-9c32-5b49-95a8-497055982343"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_cache_path("abc") == Path(
        "/nix-alien/eceff178-9c32-5b49-95a8-497055982343"
    )
