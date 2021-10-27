{ pkgs ? (import ./compat.nix).pkgs }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    fzf
    glibc
    nix-index
    poetry
  ];
}
