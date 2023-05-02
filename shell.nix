{ pkgs ? (import ./compat.nix).pkgs }:

let
  inherit (pkgs) python3 callPackage;
  nix-alien = python3.pkgs.toPythonModule (callPackage ./nix-alien.nix { dev = true; });
  python-with-packages = python3.withPackages (ps: with ps; [
    black
    mypy
    nix-alien
    pytest
  ]);
in
python-with-packages.env.overrideAttrs (old: {
  buildInputs = with pkgs; [
    fzf
    glibc.bin
    nixpkgs-fmt
    ruff
  ];
})
