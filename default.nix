{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/f112b512e1710da6c8beb8e541a8ad9fcd81e6e6.tar.gz") { }
, poetry2nix ? import (fetchTarball "https://github.com/nix-community/poetry2nix/archive/refs/tags/1.21.0.tar.gz") { inherit pkgs; poetry = pkgs.poetry; }
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
      platforms = platforms.all;
    };
  };
in
app.overrideAttrs (oldAttrs: {
  propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
    pkgs.nix-index
  ];
})
