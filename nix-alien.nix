{ lib
, fzf
, nix-index
, nix-index-database-src
, nixpkgs-src
, python3
, version
}:

let
  deps = (lib.importTOML ./src/pyproject.toml).project.dependencies;
  python3' = python3.override {
    packageOverrides = final: prev: {
      icontract = prev.icontract.overrideAttrs (oldAttrs: {
        # icontract is a dependency of pylddwrap, that has complex check
        # dependencies (astor, deal, numpy...) but almost no runtime
        # dependencies
        # Disable its tests because it often breaks builds while bringing
        # no actual advantage here
        doInstallCheck = false;
      });
      pylddwrap = prev.pylddwrap.overrideAttrs (oldAttrs: {
        # Fails to build in GitHub Actions, but works once it is build
        # in a proper aarch64 system
        doInstallCheck = false;
      });
    };
  };
in
python3'.pkgs.buildPythonApplication {
  inherit version;
  pname = "nix-alien";
  format = "pyproject";

  src = ./src;

  nativeBuildInputs = [ fzf ];

  propagatedBuildInputs = with python3'.pkgs; [
    nix-index
    setuptools
  ] ++ (lib.attrVals deps python3'.pkgs);

  preBuild = ''
    substituteInPlace nix_alien/_version.py \
      --subst-var-by version ${version} \
      --subst-var-by nixIndexDatabaseRev ${nix-index-database-src.rev or "unknown"} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev or "unknown"}
    substituteInPlace {nix_alien,tests}/*.{py,nix} \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate or "unknown"} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev or "unknown"} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash or "unknown"}
  '';

  nativeCheckInputs = with python3'.pkgs; [
    pytestCheckHook
  ];

  meta = with lib; {
    description = "Run unpatched binaries on Nix/NixOS";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
    mainProgram = "nix-alien";
    platforms = platforms.linux;
  };
}
