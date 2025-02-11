from uuid import UUID
from pathlib import Path

from nix_alien import helpers


def test_edit_file(monkeypatch):
    monkeypatch.setenv("EDITOR", "cat")
    assert helpers.edit_file(Path("/dev/null")).returncode == 0


def test_get_hash_for_program(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_hash_for_program("/home/nameless-shelter/abc") == UUID(
        "0acc4435-07de-59bf-a1c3-a42f55aaca35"
    )
    assert helpers.get_hash_for_program("~/abc") == UUID(
        "0acc4435-07de-59bf-a1c3-a42f55aaca35"
    )
    assert helpers.get_hash_for_program("/abc") == UUID(
        "cf2f97e0-6eec-5407-aea0-bbecc488d451"
    )
    assert helpers.get_hash_for_program("/./abc") == UUID(
        "cf2f97e0-6eec-5407-aea0-bbecc488d451"
    )
    assert helpers.get_hash_for_program("/xyz/../abc") == UUID(
        "cf2f97e0-6eec-5407-aea0-bbecc488d451"
    )


def test_get_cache_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_cache_path("/abc") == Path(
        "/home/nameless-shelter/.cache/nix-alien/cf2f97e0-6eec-5407-aea0-bbecc488d451"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_cache_path("/abc") == Path(
        "/nix-alien/cf2f97e0-6eec-5407-aea0-bbecc488d451"
    )


def test_get_dest_path(monkeypatch):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    assert helpers.get_dest_path(
        destination=None,
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path(
        "/home/nameless-shelter/.cache/nix-alien/cf2f97e0-6eec-5407-aea0-bbecc488d451/bar/foo.nix"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", "/")
    assert helpers.get_dest_path(
        destination=None,
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path("/nix-alien/cf2f97e0-6eec-5407-aea0-bbecc488d451/bar/foo.nix")

    assert helpers.get_dest_path(
        destination="/quux",
        program="/abc",
        directory="bar",
        filename="foo.nix",
    ) == Path("/quux/foo.nix")
