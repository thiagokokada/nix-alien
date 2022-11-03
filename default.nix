{ pkgs ? (import ./compat.nix).pkgs
, rev ? "unknown"
}:

{
  nix-alien = pkgs.callPackage ./nix-alien.nix { inherit rev; };

  nix-index-update = import ./nix-index-update.nix {
    inherit pkgs;
  };
}
