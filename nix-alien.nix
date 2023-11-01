{ lib
, fzf
, nix-filter
, nix-index
, nix-index-database-src
, nixpkgs-build-src
, nixpkgs-src
, python3
, version
}:

let
  deps = (lib.importTOML ./pyproject.toml).project.dependencies;
in
python3.pkgs.buildPythonApplication {
  inherit version;
  pname = "nix-alien";
  format = "pyproject";

  src = nix-filter.lib {
    root = ./.;
    include = [
      "nix_alien"
      "tests"
      "pyproject.toml"
      "README.md"
      "LICENSE"
    ];
  };

  nativeBuildInputs = [ fzf ];

  propagatedBuildInputs = with python3.pkgs; [
    nix-index
    setuptools
  ] ++ (lib.attrVals deps python3.pkgs);

  preBuild = ''
    substituteInPlace nix_alien/_version.py \
      --subst-var-by version ${version} \
      --subst-var-by nixIndexDatabaseRev ${nix-index-database-src.rev} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsBuildRev ${nixpkgs-build-src.rev}
    substituteInPlace {nix_alien,tests}/*.{py,nix} \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
  '';

  nativeCheckInputs = with python3.pkgs; [
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
