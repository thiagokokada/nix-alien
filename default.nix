{
  pkgs ? (import ./compat.nix).pkgs,
  self ? (import ./compat.nix).flake,
}:

let
  shortRev = self.shortRev or "dirty";
  version = "0.1.0+git_${shortRev}";
in
{
  nix-alien = pkgs.callPackage ./nix-alien.nix {
    inherit version;
    nix-index = self.inputs.nix-index-database.packages.${pkgs.system}.nix-index-with-db;
    nix-index-database-src = self.inputs.nix-index-database;
    nixpkgs-src = self.inputs.nixpkgs;
  };

  # For backwards compat, may be removed in the future
  nix-index-update = pkgs.callPackage ./nix-index-update.nix { };
}
