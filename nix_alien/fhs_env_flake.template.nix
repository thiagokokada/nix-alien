{
  description = "${__name__}-fhs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "${__system__}";
      pkgs = import nixpkgs { inherit system; };
    in
    rec {
      defaultPackage.${system} =
        let
          inherit (pkgs) buildFHSUserEnv;
        in
        buildFHSUserEnv {
          name = "${__name__}-fhs";
          targetPkgs = p: with p; [
            ${__packages__}
          ];
          runScript = "${__program__}";
        };

      defaultApp.${system} = {
        type = "app";
        program = "${defaultPackage.${system}}/bin/${__name__}-fhs";
      };
    };
}
