from pathlib import Path
from unittest.mock import call, patch

from nix_alien import fhs_shell


@patch("nix_alien.fhs_shell.find_libs")
def test_create_fhs_shell(mock_find_libs):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_shell.create_fhs_shell("xyz")
        == """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) buildFHSUserEnv;
in
buildFHSUserEnv {
  name = "xyz-fhs";
  targetPkgs = p: with p; [
    bar.out
    foo.out
    quux.out
  ];
  runScript = "%s/xyz";
}
"""
        % Path(__file__).parent.parent.absolute()
    )


@patch("nix_alien.fhs_shell.subprocess")
@patch("nix_alien.fhs_shell.find_libs")
def test_main_wo_args(mock_find_libs, mock_subprocess, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    fhs_shell.main(["xyz"])
    shell_nix = next((tmp_path / ".cache/nix-alien").glob("*/default.nix"))

    assert shell_nix.is_file()
    # Quite difficult to assert the input for the second run call here
    mock_subprocess.run.assert_called()


@patch("nix_alien.fhs_shell.subprocess")
@patch("nix_alien.fhs_shell.find_libs")
def test_main_with_args(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_shell.main(["xyz", "--destination", str(tmp_path)])
    shell_nix = tmp_path / "default.nix"
    old_stat = shell_nix.stat()

    assert shell_nix.is_file()

    fhs_shell.main(["xyz", "--destination", str(tmp_path), "--recreate"])
    new_shell_nix = tmp_path / "default.nix"

    assert new_shell_nix.stat().st_mtime_ns > old_stat.st_mtime_ns
    # Quite difficult to assert the input for the second run call here
    mock_subprocess.run.assert_called()
