{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
}:

let
  app = poetry2nix.mkPoetryApplication {
    projectDir = ./.;

    overrides = poetry2nix.overrides.withDefaults (
      final: prev: {
        pylddwrap = prev.pylddwrap.overrideAttrs (oldAttrs: {
          propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
            pkgs.glibc
          ];
        });
        pyfzf = prev.pyfzf.overrideAttrs (oldAttrs: {
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
  ];

  checkInputs = with pkgs.python3Packages; [
    pkgs.fzf
  ];

  checkPhase = ''
    # TODO: why hashlib/UUID is returning different values when building with nix?
    pytest -vvv --ignore=tests/test_helpers.py
  '';

  doCheck = true;
})
