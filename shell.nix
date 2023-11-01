{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  nix-alien = self.outputs.packages.${pkgs.system}.nix-alien.override { dev = true; };
  python-with-packages = pkgs.python3.withPackages (ps: with ps; [
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
