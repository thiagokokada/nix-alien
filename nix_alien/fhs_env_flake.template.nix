{
  description = "${__name__}-fhs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/@nixpkgsRev@";

  outputs = { self, nixpkgs }:
    let
      system = "${__system__}";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      defaultPackage.${system} =
        let
          inherit (pkgs) buildFHSEnv;
        in
        buildFHSEnv {
          name = "${__name__}-fhs";
          targetPkgs = p: with p; [
            ${__packages__}
          ];
          runScript = "${__program__}";
        };

      defaultApp.${system} = {
        type = "app";
        program = "${self.outputs.defaultPackage.${system}}/bin/${__name__}-fhs";
      };
    };
}
