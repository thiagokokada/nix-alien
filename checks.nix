{ pkgs ? (import ./compat.nix).pkgs
}:

let
  rev = "0.1.0+ci";
in
{
  nix-alien-ci = pkgs.callPackage ./nix-alien.nix {
    inherit rev;
    ci = true;
  };

  nix-index-update-ci = pkgs.callPackage ./nix-index-update.nix { };

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
