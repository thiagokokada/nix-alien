{ pkgs ? import (builtins.storePath "@nixpkgsPath@") { } }:

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
