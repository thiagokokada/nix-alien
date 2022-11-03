{
  description = "nix-alien";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs, flake-utils }:
    {
      overlays.default = final: prev: import ./default.nix {
        inherit self;
        pkgs = prev;
      };

      # For backwards compat, will be removed in the future
      overlay = self.outputs.overlays.default;
    } // (flake-utils.lib.eachSystem [ "aarch64-linux" "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };
      in
      {
        packages = {
          inherit (pkgs) nix-alien nix-index-update;
          default = self.outputs.packages.${system}.nix-alien;
        };

        checks = import ./checks.nix { inherit pkgs; };

        apps =
          let
            inherit (flake-utils.lib) mkApp;
          in
          {
            default = self.outputs.apps.${system}.nix-alien;
            nix-alien = mkApp { drv = self.outputs.packages.${system}.nix-alien; };
            nix-alien-ld = mkApp { drv = self.outputs.packages.${system}.nix-alien; name = "nix-alien-ld"; };
            nix-alien-find-libs = mkApp { drv = self.outputs.packages.${system}.nix-alien; name = "nix-alien-find-libs"; };
            nix-index-update = mkApp { drv = self.outputs.packages.${system}.nix-index-update; };
          };

        devShells.default = import ./shell.nix { inherit pkgs; };

        # For backwards compat, will be removed in the future
        defaultPackage = self.outputs.packages.${system}.default;
        defaultApp = self.outputs.apps.${system}.default;
        devShell = self.outputs.devShells.${system}.default;
      }));
}
