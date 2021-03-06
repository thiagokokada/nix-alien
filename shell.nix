{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
}:

let
  python = pkgs.python39;
  appEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    inherit python;

    editablePackageSources = {
      nix-alien = ./nix-alien;
      tests = ./tests;
    };

    overrides = poetry2nix.overrides.withDefaults (
      final: prev: {
        # Fix conflict between icontract and pylddwrap files
        icontract = prev.icontract.overrideAttrs (oldAttrs: {
          postInstall = (oldAttrs.postInstall or "") + ''
            rm -f $out/*.rst $out/*.txt
          '';
        });
      }
    );
  };
in
appEnv.env.overrideAttrs (oldAttrs: {
  buildInputs = with pkgs; [
    findutils
    fzf
    glibc.bin
    gnumake
    nix-index
    nixFlakes
    nixpkgs-fmt
    python.pkgs.poetry
  ];
})
