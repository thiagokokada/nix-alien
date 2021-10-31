from unittest.mock import patch

from nix_alien import fhs_env


@patch("nix_alien.fhs_env.find_libs")
def test_create_fhs_env_drv(mock_find_libs, pytestconfig):
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
        % pytestconfig.rootpath.absolute()
    )


@patch("nix_alien.fhs_env.find_libs")
@patch("nix_alien.nix_ld.machine")
def test_create_fhs_env_drv_flake(mock_machine, mock_find_libs, pytestconfig):
    mock_machine.return_value = "x86_64"
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_env.create_fhs_env_drv_flake("xyz")
        == """\
{
  description = "xyz-fhs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    rec {
      defaultPackage.${system} =
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
        };

      defaultApp.${system} = {
        type = "app";
        program = "${defaultPackage.${system}}/bin/xyz-fhs";
      };
    };
}
"""
        % pytestconfig.rootpath.absolute()
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

    fhs_env.main(["--destination", str(tmp_path), "--recreate", "xyz", "--foo", "bar"])
    shell_nix = tmp_path / "default.nix"

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2


@patch("nix_alien.fhs_env.subprocess")
@patch("nix_alien.fhs_env.find_libs")
def test_main_with_flake(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_env.main(["--destination", str(tmp_path), "--flake", "xyz", "--foo", "bar"])
    shell_nix = tmp_path / "flake.nix"

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 1
