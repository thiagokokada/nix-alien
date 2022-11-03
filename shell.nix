{ pkgs ? (import ./compat.nix).pkgs }:

pkgs.mkShell {
  pname = "nix-alien";

  buildInputs = with pkgs; [
    black
    mypy
  ];
}
