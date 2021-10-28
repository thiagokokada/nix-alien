from pathlib import Path
from unittest.mock import patch

from nix_alien import fhs_env


@patch("nix_alien.fhs_env.find_libs")
def test_create_fhs_env(mock_find_libs):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_env.create_fhs_env_drv("xyz")
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


@patch("nix_alien.fhs_env.subprocess")
@patch("nix_alien.fhs_env.find_libs")
def test_main_wo_args(mock_find_libs, mock_subprocess, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    fhs_env.main(["xyz"])
    shell_nix = next((tmp_path / ".cache/nix-alien").glob("*/fhs-env/default.nix"))

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2


@patch("nix_alien.fhs_env.subprocess")
@patch("nix_alien.fhs_env.find_libs")
def test_main_with_args(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_env.main(["xyz", "--destination", str(tmp_path), "--recreate"])
    shell_nix = tmp_path / "default.nix"

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2
