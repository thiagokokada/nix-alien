{ pkgs ? (import ./compat.nix).pkgs
, self ? (import ./compat.nix).flake
}:

let
  rev = "0.1.0+ci";
in
{
  nix-alien-ci = pkgs.callPackage ./nix-alien.nix {
    ci = true;
    inherit rev;
    nix-index = self.inputs.nix-index-database.packages.${pkgs.system}.nix-index-with-db;
    nixpkgs-input = self.inputs.nix-index-database.inputs.nixpkgs.sourceInfo;
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
