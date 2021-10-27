{ pkgs ? (import ./compat.nix).pkgs }:

pkgs.mkShell {
  buildInputs = with pkgs; [ poetry ];
}
