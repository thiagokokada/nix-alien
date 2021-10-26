{
  description = "nix-alien";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          nix-alien = import ./default.nix {
            nixpkgs = prev;
            inherit (prev) poetry2nix;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      rec {
        packages.nix-alien = pkgs.nix-alien;
        defaultPackage = self.packages.${system}.nix-alien;

        apps =
          let
            inherit (flake-utils.lib) mkApp;
          in
          {
            nix-alien = mkApp { drv = pkgs.nix-alien; };
            nix-alien-ld = mkApp { drv = pkgs.nix-alien; name = "nix-alien-ld"; };
            nix-alien-find-libs = mkApp { drv = pkgs.nix-alien; name = "nix-alien-find-libs"; };
          };

        defaultApp = apps.nix-alien;

        devShell = import ./shell.nix { inherit pkgs; };
      }));
}
