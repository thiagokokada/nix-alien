{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
  # TODO: make it work with non-flakes
, rev ? "unknown"
}:

let
  app = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    python = pkgs.python39;

    overrides = poetry2nix.overrides.withDefaults (
      final: prev: {
        pylddwrap = prev.pylddwrap.overrideAttrs (oldAttrs: {
          propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
            pkgs.glibc.bin
          ];
        });
        python-fzf = prev.python-fzf.overrideAttrs (oldAttrs: {
          propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
            pkgs.fzf
          ];
        });
      }
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
    pkgs.nixUnstable
  ];

  preBuild = ''
    echo "__version__ = '${rev}'" > nix_alien/_version.py
  '';

  checkPhase = ''
    mypy --ignore-missing-imports .
    pytest -vvv
  '';

  doCheck = true;
})
