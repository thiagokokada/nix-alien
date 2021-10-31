from uuid import UUID
from pathlib import Path

from nix_alien import helpers


def test_get_hash_for_program(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_hash_for_program("/home/nameless-shelter/abc") == UUID(
        "d0efaea7-176f-56e6-99a0-ea49599a163b"
    )
    assert helpers.get_hash_for_program("~/abc") == UUID(
        "d0efaea7-176f-56e6-99a0-ea49599a163b"
    )
    assert helpers.get_hash_for_program("/abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
    assert helpers.get_hash_for_program("/./abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
    )
    assert helpers.get_hash_for_program("/xyz/../abc") == UUID(
        "f52177f5-def5-5d9e-91fc-ef1283fc54b1"
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


def test_get_dest_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")

    assert helpers.get_dest_path(
        destination=None,
        program="/bin/foo",
        directory="bar",
        filename="foo.nix",
    ) == Path(
        "/home/nameless-shelter/.cache/nix-alien/871184f9-aad6-5705-bdb5-6f10f378d3df/bar/foo.nix"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_dest_path(
        destination=None,
        program="/bin/foo",
        directory="bar",
        filename="foo.nix",
    ) == Path(
        "/nix-alien/871184f9-aad6-5705-bdb5-6f10f378d3df/bar/foo.nix"
    )

    assert (
        helpers.get_dest_path(
            destination="/quux",
            program="/bin/foo",
            directory="bar",
            filename="foo.nix",
        )
        == Path("/quux/foo.nix")
    )
