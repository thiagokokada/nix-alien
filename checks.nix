{ pkgs ? (import ./compat.nix).pkgs
, rev ? "ci"
}:

{
  nix-alien-ci = pkgs.callPackage ./nix-alien.nix {
    inherit rev;
    ci = true;
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
