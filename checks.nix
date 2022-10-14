{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
, rev ? "ci"
}:

{
  nix-alien-ci = import ./nix-alien.nix {
    inherit pkgs poetry2nix rev;
    ci = true;
  };

  nix-alien-ci-py39 = import ./nix-alien.nix {
    inherit pkgs poetry2nix rev;
    ci = true;
    python = pkgs.python39;
  };

  nix-index-update-ci = import ./nix-index-update.nix {
    inherit pkgs;
  };

  check-format-nix = pkgs.runCommand "check-format-nix"
    {
      src = ./.;
      nativeBuildInputs = [ pkgs.nixpkgs-fmt ];
    } ''
    touch $out
    nixpkgs-fmt --check $src
  '';
}
