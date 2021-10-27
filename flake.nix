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
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          nix-alien = import ./default.nix {
            inherit (final) poetry2nix;
            pkgs = final;
          };
          nix-index-update = import ./nix-index-update.nix {
            pkgs = final;
            system = final.system;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
        poetry2nix' = import poetry2nix {
          inherit pkgs;
          poetry = pkgs.poetry;
        };
      in
      rec {
        packages = {
          nix-alien = pkgs.nix-alien;
          nix-index-update = pkgs.nix-index-update;
        };

        defaultPackage = packages.nix-alien;

        apps =
          let
            inherit (flake-utils.lib) mkApp;
          in
          {
            nix-alien = mkApp { drv = packages.nix-alien; };
            nix-alien-ld = mkApp { drv = packages.nix-alien; name = "nix-alien-ld"; };
            nix-alien-find-libs = mkApp { drv = packages.nix-alien; name = "nix-alien-find-libs"; };
            nix-index-update = mkApp { drv = packages.nix-index-update; name = "nix-index-update"; };
          };

        defaultApp = apps.nix-alien;

        devShell = import ./shell.nix {
          inherit pkgs;
          poetry2nix = poetry2nix';
        };
      }));
}
