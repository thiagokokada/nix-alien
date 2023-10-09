# Compatibility with non-flakes systems
let
  flakeLock = builtins.fromJSON (builtins.readFile ./flake.lock);
in
rec {
  flake =
    (import
      (
        let lock = with builtins; fromJSON (readFile ./flake.lock); in
        builtins.fetchTarball {
          url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
          sha256 = lock.nodes.flake-compat.locked.narHash;
        }
      )
      { src = ./.; }).defaultNix;

  pkgs = import flake.inputs.nixpkgs { };
}
