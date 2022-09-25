{ pkgs ? (import ./compat.nix).pkgs }:

let
  inherit (pkgs) coreutils stdenv substituteAll system wget;
in
stdenv.mkDerivation {
  name = "nix-index-update";

  src = substituteAll {
    src = ./nix-index-update.sh;
    isExecutable = true;
    inherit coreutils wget system;
  };

  dontUnpack = true;

  installPhase = ''
    install -Dm755 "$src" "$out/bin/nix-index-update"
  '';

}
