{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  inherit (self.inputs) nix-filter;
in
rec {
  inherit (self.outputs.packages.${pkgs.system}) nix-alien nix-index-update;

  check-py-files = pkgs.runCommand "check-py-files"
    {
      inherit (nix-alien) src;
      nativeBuildInputs = with pkgs; [
        python3.pkgs.mypy
        ruff
      ];
    } ''
    touch $out
    export PYLINTHOME="$(mktemp -d)"
    export RUFF_CACHE_DIR="$(mktemp -d)"
    mypy --ignore-missing-imports $src/nix_alien
    ruff format --check $src/nix_alien
    ruff check $src/nix_alien
  '';

  check-nix-files = pkgs.runCommand "check-nix-files"
    {
      src = nix-filter.lib {
        root = ./.;
        include = [ (nix-filter.lib.matchExt "nix") ];
      };
      nativeBuildInputs = with pkgs; [ nixpkgs-fmt statix ];
    } ''
    touch $out
    nixpkgs-fmt --check $src
    statix check $src
  '';
}
