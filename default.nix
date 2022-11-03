{ pkgs ? (import ./compat.nix).pkgs
, self ? { }
}:

let
  dirty =
    if (self ? rev)
    then ""
    else "_dirty";
  rev =
    if (self ? lastModifiedDate)
    then "0.1.0+git${self.lastModifiedDate}${dirty}"
    else "0.1.0+unknown";
in
{
  nix-alien = pkgs.callPackage ./nix-alien.nix { inherit rev; };

  nix-index-update = pkgs.callPackage ./nix-index-update.nix { };
}
