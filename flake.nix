{
  description = "nix-alien";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      overlays.default = final: prev: import ./default.nix {
        poetry2nix = (poetry2nix.overlay final prev).poetry2nix;
        # FIXME: using `prev` here results in a glibc rebuild on every Python deps change
        pkgs = final;
        rev = if (self ? rev) then self.rev else "dirty";
      };

      # For backwards compat, will be removed in the future
      overlay = self.outputs.overlays.default;
    } // (flake-utils.lib.eachSystem [ "aarch64-linux" "i686-linux" "x86_64-linux" ] (system:
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

        checks.nix-alien-ci = pkgs.nix-alien.override {
          ci = true;
        };

        apps =
          let
            inherit (flake-utils.lib) mkApp;
          in
          {
            default = self.outputs.apps.${system}.nix-alien;
            nix-alien = mkApp { drv = self.outputs.${system}.packages.nix-alien; };
            nix-alien-ld = mkApp { drv = self.outputs.${system}.packages.nix-alien; name = "nix-alien-ld"; };
            nix-alien-find-libs = mkApp { drv = self.outputs.${system}.packages.nix-alien; name = "nix-alien-find-libs"; };
            nix-index-update = mkApp { drv = self.outputs.${system}.packages.nix-index-update; };
          };

        devShells.default = import ./shell.nix {
          inherit pkgs;
          inherit (pkgs) poetry2nix;
        };

        # For backwards compat, will be removed in the future
        defaultPackage = self.outputs.packages.${system}.default;
        defaultApp = self.outputs.apps.${system}.default;
        devShell = self.outputs.devShells.${system}.default;
      }));
}
