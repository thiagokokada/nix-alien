{
  description = "nix-alien";

  inputs = {
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-index-database.url = "github:Mic92/nix-index-database";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    {
      overlays.default = final: prev: import ./overlay.nix { inherit self final prev; };
    } // (flake-utils.lib.eachSystem [ "aarch64-linux" "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };
      in
      {
        formatter = pkgs.nixpkgs-fmt;

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
      }));
}
