# Compatibility with non-flakes systems
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
