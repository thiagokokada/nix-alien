# Compatibility with non-flakes systems
let
  flakeLock = (builtins.fromJSON (builtins.readFile ./flake.lock));
in
rec {
  pkgs =
    let
      inherit (flakeLock.nodes.nixpkgs.locked) rev narHash;
    in
    import
      (fetchTarball {
        url = "https://github.com/NixOS/nixpkgs/archive/${rev}.tar.gz";
        sha256 = narHash;
      })
      { };
  poetry2nix =
    let
      inherit (flakeLock.nodes.poetry2nix.locked) rev narHash;
    in
    import
      (fetchTarball {
        url = "https://github.com/nix-community/poetry2nix/archive/${rev}.tar.gz";
        sha256 = narHash;
      })
      {
        inherit pkgs;
        poetry = pkgs.poetry;
      };
}
