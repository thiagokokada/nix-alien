from unittest.mock import patch

from nix_alien import ld_shell


def test_create_ld_shell():
    with patch("nix_alien.ld_shell.find_libs") as mock_find_libs:
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
