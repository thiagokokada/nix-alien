{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

{
  inherit (self.outputs.packages.${pkgs.system}) nix-alien nix-index-update;

  check-py-files = pkgs.runCommand "check-py-files"
    {
      src = ./.;
      nativeBuildInputs = with pkgs; [
        python3.pkgs.black
        python3.pkgs.mypy
        ruff
      ];
    } ''
    touch $out
    export PYLINTHOME="$(mktemp -d)"
    export RUFF_CACHE_DIR="$(mktemp -d)"
    black --check $src/nix_alien
    mypy --ignore-missing-imports $src/nix_alien
    ruff check $src/nix_alien
  '';

  check-nix-files = pkgs.runCommand "check-nix-files"
    {
      src = ./.;
      nativeBuildInputs = with pkgs; [ nixpkgs-fmt statix ];
    } ''
    touch $out
    nixpkgs-fmt --check $src
    statix check $src
  '';
}
