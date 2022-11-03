{ pkgs ? (import ./compat.nix).pkgs
, rev ? "unknown"
}:

{
  nix-alien = pkgs.callPackage ./nix-alien.nix { inherit rev; };

  nix-index-update = pkgs.callPackage ./nix-index-update.nix { };
}
