{
  description = "${__name__}-nix-ld";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "${__system__}";
      pkgs = import nixpkgs { inherit system; };
    in
    rec {
      defaultPackage.${system} =
        let
          inherit (pkgs) lib stdenv;
          NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
            ${__packages__}
          ];
          NIX_LD = "${stdenv.cc}/nix-support/dynamic-linker";
        in
        pkgs.writeShellScriptBin "${__name__}" ''
          export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
          export NIX_LD="$(< ${NIX_LD})"${"\${NIX_LD:+':'}$NIX_LD"}
          "${__program__}" "$@"
        '';

      defaultApp.${system} = {
        type = "app";
        program = "${defaultPackage.${system}}/bin/${__name__}";
      };
    };
}
