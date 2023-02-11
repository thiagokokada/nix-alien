from unittest.mock import patch

from nix_alien import fhs_env


@patch("nix_alien._impl.find_libs")
def test_create_fhs_env_drv(mock_find_libs, pytestconfig):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_env.create_fhs_env_drv("xyz", additional_packages=["libGL"])
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
    libGL
  ];
  runScript = "%s/xyz";
}
"""
        % pytestconfig.rootpath.absolute()
    )


@patch("nix_alien._impl.find_libs")
@patch("nix_alien._impl.machine")
def test_create_fhs_env_drv_flake(mock_machine, mock_find_libs, pytestconfig):
    mock_machine.return_value = "x86_64"
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_env.create_fhs_env_drv_flake("xyz", additional_packages=["libGL"])
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
            libGL
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


@patch("nix_alien._impl.subprocess")
@patch("nix_alien._impl.os")
@patch("nix_alien._impl.find_libs")
def test_main_wo_args(
    mock_find_libs,
    mock_os,
    mock_subprocess,
    monkeypatch,
    tmp_path,
    capsys,
):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    fhs_env.main(["xyz"])
    default_nix = next((tmp_path / ".cache/nix-alien").glob("*/fhs-env/default.nix"))

    assert default_nix.is_file()
    assert mock_subprocess.run.call_count == 1
    assert mock_os.execv.call_count == 1

    _, err = capsys.readouterr()
    # Not showing messages from find_libs since it is mocked
    assert (
        err
        == f"""\
[nix-alien] File '{default_nix}' created successfuly!
"""
    )


@patch("nix_alien._impl.subprocess")
@patch("nix_alien._impl.os")
@patch("nix_alien._impl.find_libs")
def test_main_with_args(
    mock_find_libs,
    mock_os,
    mock_subprocess,
    tmp_path,
    capsys,
):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_env.main(
        [
            "--destination",
            str(tmp_path),
            "--silent",
            "--recreate",
            "xyz",
            "--foo",
            "bar",
        ]
    )
    default_nix = tmp_path / "default.nix"

    assert default_nix.is_file()
    assert mock_subprocess.run.call_count == 1
    assert mock_os.execv.call_count == 1

    _, err = capsys.readouterr()
    assert err == ""


@patch("nix_alien._impl.os")
@patch("nix_alien._impl.find_libs")
def test_main_with_flake(mock_find_libs, mock_os, tmp_path, capsys):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_env.main(["--destination", str(tmp_path), "--flake", "xyz", "--foo", "bar"])
    flake_nix = tmp_path / "flake.nix"

    assert flake_nix.is_file()
    assert mock_os.execvp.call_count == 1

    _, err = capsys.readouterr()
    # Not showing messages from find_libs since it is mocked
    assert (
        err
        == f"""\
[nix-alien] File '{flake_nix}' created successfuly!
"""
    )


def test_main_with_print(monkeypatch, capsys):
    monkeypatch.setenv("HOME", "/home/nameless-shelter")
    fhs_env.main(["--print", "/xyz"])

    out, _ = capsys.readouterr()
    assert (
        out
        == """\
/home/nameless-shelter/.cache/nix-alien/b5ae45f6-276c-53a3-93ab-4a44f35976a4/fhs-env/default.nix
"""
    )

    fhs_env.main(["--flake", "--print", "/xyz"])

    out, _ = capsys.readouterr()
    assert (
        out
        == """\
/home/nameless-shelter/.cache/nix-alien/b5ae45f6-276c-53a3-93ab-4a44f35976a4/fhs-env/flake.nix
"""
    )
