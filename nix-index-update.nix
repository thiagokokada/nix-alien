{ pkgs ? (import ./compat.nix).pkgs
, system ? builtins.currentSystem
}:

let
  inherit (pkgs) stdenv coreutils wget;
in
stdenv.mkDerivation {
  name = "nix-index-update";

  src = with pkgs; substituteAll {
    src = ./nix-index-update.sh;
    isExecutable = true;
    inherit coreutils wget system;
  };

  dontUnpack = true;

  installPhase = ''
    install -Dm755 "$src" "$out/bin/nix-index-update"
  '';

}
