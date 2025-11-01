{
  pkgs ? (import ./compat.nix).pkgs,
  self ? (import ./compat.nix).flake,
}:

rec {
  inherit (self.outputs.packages.${pkgs.stdenv.hostPlatform.system}) nix-alien nix-index-update;

  check-py-files =
    pkgs.runCommand "check-py-files"
      {
        inherit (nix-alien) src;
        nativeBuildInputs = with pkgs; [
          python3.pkgs.mypy
          ruff
        ];
      }
      ''
        export PYLINTHOME="$(mktemp -d)"
        export RUFF_CACHE_DIR="$(mktemp -d)"
        mypy --ignore-missing-imports $src/nix_alien
        ruff check $src/nix_alien
        touch $out
      '';

  check-format =
    pkgs.runCommand "check-format"
      {
        src = ./.;
        nativeBuildInputs = with pkgs; [
          treefmt
          ruff
          nixfmt-rfc-style
        ];
      }
      ''
        export RUFF_CACHE_DIR="$(mktemp -d)"
        cd $src
        treefmt --ci
        touch $out
      '';
}
