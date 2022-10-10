{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
, rev ? "unknown"
}:

{
  nix-alien = import ./nix-alien.nix {
    inherit pkgs poetry2nix rev;
  };

  nix-index-update = import ./nix-index-update.nix {
    inherit pkgs;
  };

  check-format-nix = pkgs.stdenv.mkDerivation {
    name = "check-format-nix";
    src = ./.;
    nativeBuildInputs = [ pkgs.nixpkgs-fmt ];

    dontConfigure = true;
    dontBuild = true;
    doCheck = true;

    installPhase = "touch $out";

    checkPhase = ''
      nixpkgs-fmt --check .
    '';
  };
}
