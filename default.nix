{ pkgs ? (import ./compat.nix).pkgs
, self ? { }
}:

let
  inherit (pkgs) lib;
  flake =
    if (self == { }) then
      (import
        (
          let lock = with builtins; fromJSON (readFile ./flake.lock); in
          builtins.fetchTarball {
            url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
            sha256 = lock.nodes.flake-compat.locked.narHash;
          }
        )
        { src = ./.; }).defaultNix
    else self;
  dirty = lib.optionalString (!(flake ? rev)) "_dirty";
  rev = "0.1.0+git${flake.lastModifiedDate}${dirty}";
in
{
  nix-alien = pkgs.callPackage ./nix-alien.nix {
    inherit rev;
    nix-index = flake.inputs.nix-index-database.packages.${pkgs.system}.nix-index-with-db;
  };

  # For backwards compat, may be removed in the future
  nix-index-update = pkgs.callPackage ./nix-index-update.nix { };
}
