{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  inherit (pkgs) python3 callPackage;
  nix-alien = python3.pkgs.toPythonModule (callPackage ./nix-alien.nix {
    dev = true;
    inherit (self.inputs) nix-filter;
    nix-index = self.inputs.nix-index-database.packages.${pkgs.system}.nix-index-with-db;
    nixpkgs-src = self.inputs.nix-index-database.inputs.nixpkgs.sourceInfo;
  });
  python-with-packages = python3.withPackages (ps: with ps; [
    black
    mypy
    nix-alien
    pytest
  ]);
in
python-with-packages.env.overrideAttrs (old: {
  buildInputs = with pkgs; [
    nixpkgs-fmt
    ruff
    statix
  ];
})
