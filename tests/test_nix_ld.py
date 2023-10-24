from unittest.mock import patch

from nix_alien import nix_ld


@patch("nix_alien._impl.find_libs")
def test_create_nix_ld_drv(mock_find_libs, pytestconfig):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        nix_ld.create_nix_ld_drv("xyz", additional_packages=["libGL"])
        == """\
{ pkgs ? import
    (builtins.fetchTarball {
      name = "nixpkgs-unstable-@nixpkgsLastModifiedDate@";
      url = "https://github.com/NixOS/nixpkgs/archive/@nixpkgsRev@.tar.gz";
      sha256 = "@nixpkgsHash@";
    })
    { }
}:

let
  inherit (pkgs) lib stdenv;
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    bar.out
    foo.out
    quux.out
    libGL
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
in
pkgs.writeShellScriptBin "xyz" ''
  export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
  export NIX_LD='${NIX_LD}'
  %s/xyz "$@"
''
"""
        % pytestconfig.rootpath.absolute()
    )


@patch("nix_alien._impl.find_libs")
def test_create_nix_ld_drv_with_spaces(mock_find_libs, pytestconfig):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        nix_ld.create_nix_ld_drv("x y z", additional_packages=["libGL"])
        == """\
{ pkgs ? import
    (builtins.fetchTarball {
      name = "nixpkgs-unstable-@nixpkgsLastModifiedDate@";
      url = "https://github.com/NixOS/nixpkgs/archive/@nixpkgsRev@.tar.gz";
      sha256 = "@nixpkgsHash@";
    })
    { }
}:

let
  inherit (pkgs) lib stdenv;
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    bar.out
    foo.out
    quux.out
    libGL
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
in
pkgs.writeShellScriptBin "x_y_z" ''
  export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
  export NIX_LD='${NIX_LD}'
  '%s/x y z' "$@"
''
"""
        % pytestconfig.rootpath.absolute()
    )


@patch("nix_alien._impl.find_libs")
@patch("nix_alien._impl.machine")
def test_create_nix_ld_drv_flake(mock_machine, mock_find_libs, pytestconfig):
    mock_machine.return_value = "x86_64"
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        nix_ld.create_nix_ld_drv_flake("xyz", additional_packages=["libGL"])
        == """\
{
  description = "xyz-nix-ld";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/@nixpkgsRev@";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    rec {
      defaultPackage.${system} =
        let
          inherit (pkgs) lib stdenv;
          NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
            bar.out
            foo.out
            quux.out
            libGL
          ];
        in
        pkgs.writeShellScriptBin "xyz" ''
          export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
          export NIX_LD="$(cat ${stdenv.cc}/nix-support/dynamic-linker)"
          %s/xyz "$@"
        '';

      defaultApp.${system} = {
        type = "app";
        program = "${defaultPackage.${system}}/bin/xyz";
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
    nix_ld.main(["xyz"])
    default_nix = next((tmp_path / ".cache/nix-alien").glob("*/nix-ld/default.nix"))

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

    nix_ld.main(
        [
            "--destination",
            str(tmp_path),
            "--recreate",
            "--silent",
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

    nix_ld.main(["--destination", str(tmp_path), "--flake", "xyz", "--foo", "bar"])
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
    nix_ld.main(["--print", "/xyz"])

    out, _ = capsys.readouterr()
    assert (
        out
        == """\
/home/nameless-shelter/.cache/nix-alien/d51a223b-43f0-56c6-b5c8-2404823026ac/nix-ld/default.nix
"""
    )

    nix_ld.main(["--flake", "--print", "/xyz"])

    out, _ = capsys.readouterr()
    assert (
        out
        == """\
/home/nameless-shelter/.cache/nix-alien/d51a223b-43f0-56c6-b5c8-2404823026ac/nix-ld/flake.nix
"""
    )
