{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  inherit (pkgs) python3;
  nix-alien = python3.pkgs.toPythonModule
    (self.outputs.packages.${pkgs.system}.nix-alien.overrideAttrs
      (oldAttrs: { doInstallCheck = false; }));
  python-with-packages = python3.withPackages (ps: with ps; [
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
