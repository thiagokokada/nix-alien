{
  description = "nix-alien";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.poetry2nix ={
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        poetry2nix' = import poetry2nix {
          inherit pkgs;
          poetry = pkgs.poetry;
        };
      in
      rec {
        packages = {
          nix-alien = import ./default.nix {
            inherit pkgs;
            poetry2nix = poetry2nix';
          };

          nix-index-update =
            let
              inherit (pkgs) coreutils wget;
            in
            pkgs.writeShellScriptBin "nix-index-update" ''
              set -euo pipefail

              readonly filename="index-${system}"
              readonly dest_dir="$HOME/.cache/nix-index"

              ${coreutils}/bin/mkdir -p "$dest_dir"
              pushd "$dest_dir" >/dev/null
              trap "popd >/dev/null" EXIT

              # -N will only download a new version if there is an update.
              ${wget}/bin/wget -q -N "https://github.com/Mic92/nix-index-database/releases/latest/download/$filename"
              ${coreutils}/bin/ln -f "$filename" files

              echo "Done!"
            '';
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

        devShell = import ./shell.nix { inherit pkgs; };
      }));
}
