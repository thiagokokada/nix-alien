from unittest.mock import call, patch

from nix_alien import ld_shell


@patch("nix_alien.ld_shell.find_libs")
def test_create_ld_shell(mock_find_libs):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        ld_shell.create_ld_shell("xyz")
        == """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) mkShell lib stdenv;
in
mkShell {
  name = "xyz-ld-shell";
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    bar.out
    foo.out
    quux.out
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
}
"""
    )


@patch("nix_alien.ld_shell.subprocess")
@patch("nix_alien.ld_shell.find_libs")
def test_main_wo_args(mock_find_libs, mock_subprocess, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    ld_shell.main(["xyz"])
    shell_nix = next((tmp_path / ".cache/nix-alien").glob("*/shell.nix"))

    assert shell_nix.is_file()
    mock_subprocess.run.assert_called_once_with(["nix-shell", str(shell_nix)])


@patch("nix_alien.ld_shell.subprocess")
@patch("nix_alien.ld_shell.find_libs")
def test_main_with_args(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    ld_shell.main(["xyz", "--destination", str(tmp_path)])
    shell_nix = tmp_path / "shell.nix"
    old_stat = shell_nix.stat()

    assert shell_nix.is_file()

    ld_shell.main(["xyz", "--destination", str(tmp_path), "--recreate"])
    new_shell_nix = tmp_path / "shell.nix"

    assert new_shell_nix.stat().st_mtime_ns > old_stat.st_mtime_ns
    mock_subprocess.run.assert_has_calls(
        [
            call(["nix-shell", str(shell_nix)]),
            call(["nix-shell", str(shell_nix)]),
        ]
    )
