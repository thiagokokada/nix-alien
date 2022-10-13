{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
, python ? pkgs.python310
  # TODO: make it work with non-flakes
, rev ? "unknown"
, ci ? false
}:

let
  app = poetry2nix.mkPoetryApplication rec {
    projectDir = ./.;
    inherit python;

    overrides = poetry2nix.overrides.withDefaults (
      final: prev:
        (import ./overrides.nix pkgs final prev)
        // (pkgs.lib.optionalAttrs (!ci) {
          # We want to run tests in non-CI builds but not black/mypy
          black = pkgs.writeShellScriptBin "black" "exit 0";
          mypy = pkgs.writeShellScriptBin "mypy" "exit 0";
        })
    );

    meta = with pkgs.lib; {
      description = "Run unpatched binaries on Nix/NixOS";
      homepage = "https://github.com/thiagokokada/nix-alien";
      license = licenses.mit;
      platforms = platforms.linux;
    };
  };
in
app.overrideAttrs (oldAttrs: {
  propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
    pkgs.nix-index
    pkgs.nixVersions.stable
  ];

  preBuild = ''
    echo "__version__ = \"${rev}\"" > nix_alien/_version.py
  '';

  checkInputs = [
    pkgs.fzf
  ];

  checkPhase = ''
    runHook preCheck

    black --check .
    mypy --ignore-missing-imports .
    pytest -vvv

    runHook postCheck
  '';

  doCheck = true;
})
