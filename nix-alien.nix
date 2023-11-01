{ lib
, fzf
, nix-index
, nix-filter
, nixpkgs-src ? {
    lastModifiedDate = "19700101000000";
    rev = "nixpkgs-unstable";
    narHash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  }
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
    echo "__version__ = \"${version}\"" > nix_alien/_version.py
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
