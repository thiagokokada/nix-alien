from uuid import UUID
from pathlib import Path

from nix_alien import helpers


def test_edit_file(monkeypatch):
    monkeypatch.setenv("EDITOR", "cat")
    assert helpers.edit_file(Path("/dev/null")).returncode == 0


def test_get_hash_for_program(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_hash_for_program("/home/nameless-shelter/abc") == UUID(
        "c5daaed5-c070-5203-b7a7-e0015b58cbe6"
    )
    assert helpers.get_hash_for_program("~/abc") == UUID(
        "c5daaed5-c070-5203-b7a7-e0015b58cbe6"
    )
    assert helpers.get_hash_for_program("/abc") == UUID(
        "addde828-d418-5484-92de-fe0fc60a7410"
    )
    assert helpers.get_hash_for_program("/./abc") == UUID(
        "addde828-d418-5484-92de-fe0fc60a7410"
    )
    assert helpers.get_hash_for_program("/xyz/../abc") == UUID(
        "addde828-d418-5484-92de-fe0fc60a7410"
    )


def test_get_cache_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_cache_path("/abc") == Path(
        "/home/nameless-shelter/.cache/nix-alien/addde828-d418-5484-92de-fe0fc60a7410"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_cache_path("/abc") == Path(
        "/nix-alien/addde828-d418-5484-92de-fe0fc60a7410"
    )


def test_get_dest_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_dest_path(
        destination=None,
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path(
        "/home/nameless-shelter/.cache/nix-alien/addde828-d418-5484-92de-fe0fc60a7410/bar/foo.nix"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_dest_path(
        destination=None,
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path("/nix-alien/addde828-d418-5484-92de-fe0fc60a7410/bar/foo.nix")

    assert helpers.get_dest_path(
        destination="/quux",
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path("/quux/foo.nix")
