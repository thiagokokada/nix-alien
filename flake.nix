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
      overlay = final: prev: import ./default.nix {
        inherit (prev.stdenv.hostPlatform) system;
        poetry2nix = (poetry2nix.overlay final prev).poetry2nix;
        pkgs = prev;
        rev = if (self ? rev) then self.rev else "dirty";
      };
    } // (flake-utils.lib.eachSystem [ "aarch64-linux" "i686-linux" "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      rec {
        packages = { inherit (pkgs) _nix-alien-ci nix-alien nix-index-update; };

        defaultPackage = packages.nix-alien;

        apps =
          let
            inherit (flake-utils.lib) mkApp;
          in
          {
            nix-alien = mkApp { drv = packages.nix-alien; };
            nix-alien-ld = mkApp { drv = packages.nix-alien; name = "nix-alien-ld"; };
            nix-alien-find-libs = mkApp { drv = packages.nix-alien; name = "nix-alien-find-libs"; };
            nix-index-update = mkApp { drv = packages.nix-index-update; };
          };

        defaultApp = apps.nix-alien;

        devShell = import ./shell.nix {
          inherit pkgs;
          inherit (pkgs) poetry2nix;
        };
      }));
}
