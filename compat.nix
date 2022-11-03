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
}
