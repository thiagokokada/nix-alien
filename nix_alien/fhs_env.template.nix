{ pkgs ? import
    (builtins.fetchTarball {
      name = "nixpkgs-unstable-@nixpkgsLastModifiedDate@";
      url = "https://github.com/NixOS/nixpkgs/archive/@nixpkgsRev@.tar.gz";
      sha256 = "@nixpkgsHash@";
    })
    { }
}:

let
  inherit (pkgs) buildFHSEnv;
in
buildFHSEnv {
  name = "${__name__}-fhs";
  targetPkgs = p: with p; [
    ${__packages__}
  ];
  runScript = "${__program__}";
}
