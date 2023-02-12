{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  inherit (pkgs) lib;
  dirty = lib.optionalString (!(self ? rev)) "_dirty";
  rev = "0.1.0+git${self.lastModifiedDate}${dirty}";
in
{
  nix-alien = pkgs.callPackage ./nix-alien.nix {
    inherit rev;
    nix-index = self.inputs.nix-index-database.packages.${pkgs.system}.nix-index-with-db;
  };

  # For backwards compat, may be removed in the future
  nix-index-update = pkgs.callPackage ./nix-index-update.nix { };
}
