{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
, python ? pkgs.python310
}:

let
  appEnv = pkgs.poetry2nix.mkPoetryEnv {
    inherit python;

    projectDir = ./.;

    editablePackageSources = {
      nix-alien = ./nix-alien;
      tests = ./tests;
    };

    overrides = poetry2nix.overrides.withDefaults (
      (import ./overrides.nix pkgs)
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
    nixVersions.stable
    nixpkgs-fmt
    python.pkgs.poetry
  ];

  # TODO: remove once this issue is fixed:
  # https://github.com/python-poetry/poetry/issues/1917
  PYTHON_KEYRING_BACKEND = "keyring.backends.null.Keyring";
})
