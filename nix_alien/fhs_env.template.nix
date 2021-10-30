{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) buildFHSUserEnv;
in
buildFHSUserEnv {
  name = "${__name__}-fhs";
  targetPkgs = p: with p; [
    ${__packages__}
  ];
  runScript = "${__program__}";
}
