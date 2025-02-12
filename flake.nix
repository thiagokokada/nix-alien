{
  description = "nix-alien";

  inputs = {
    flake-compat.url = "github:edolstra/flake-compat";
    nix-index-database = {
      url = "github:nix-community/nix-index-database";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      overlay = final: prev: import ./overlay.nix { inherit self final prev; };

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      # Helper function to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'.
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Nixpkgs instantiated for supported system types.
      nixpkgsFor = forAllSystems (
        system:
        import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        }
      );
    in
    {
      overlays.default = final: prev: import ./overlay.nix { inherit self final prev; };

      # Integration tests are only available in x86_64-linux for now
      integration-tests.x86_64-linux = import ./integration-tests.nix { inherit self; };

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        import ./checks.nix { inherit pkgs self; }
      );

      formatter = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
          inherit (pkgs) lib;
        in
        # Not using treefmt-nix to avoid an additional dependency in Flake
        pkgs.writeShellScriptBin "treefmt-with-deps" ''
          export PATH="${
            lib.makeBinPath [
              pkgs.ruff
              pkgs.nixfmt-rfc-style
            ]
          }"
          ${lib.getExe pkgs.treefmt}
        ''
      );

      apps = forAllSystems (
        system:
        let
          genNixAlienApp = name: {
            type = "app";
            program = nixpkgs.lib.getExe' self.packages.${system}.nix-alien name;
          };
        in
        {
          default = self.outputs.apps.${system}.nix-alien;
          nix-alien = genNixAlienApp "nix-alien";
          nix-alien-ld = genNixAlienApp "nix-alien-ld";
          nix-alien-find-libs = genNixAlienApp "nix-alien-find-libs";
        }
      );

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          inherit (pkgs) nix-alien nix-index-update;
          default = self.outputs.packages.${system}.nix-alien;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          default = import ./shell.nix { inherit pkgs self; };
        }
      );
    };
}
