{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
, rev ? "unknown"
, system ? builtins.currentSystem
, ...
}:

{
  _nix-alien-ci = import ./nix-alien.nix {
    inherit pkgs poetry2nix rev;
    ci = true;
  };
  nix-alien = import ./nix-alien.nix {
    inherit pkgs poetry2nix rev;
  };
  nix-index-update = import ./nix-index-update.nix {
    inherit pkgs system;
  };
}
