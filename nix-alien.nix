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
, rev ? null
, dev ? false
}:

let
  version = if (rev != null) then rev else "dev";
  deps = (lib.importTOML ./pyproject.toml).project.dependencies;
in
python3.pkgs.buildPythonApplication {
  pname = "nix-alien";
  format = "pyproject";
  inherit version;

  src = nix-filter.lib {
    root = ./.;
    include = [ "nix_alien" "tests" "pyproject.toml" "README.md" ];
  };

  nativeBuildInputs = [ fzf ];

  propagatedBuildInputs = with python3.pkgs; [
    nix-index
    setuptools
  ] ++ (lib.attrVals deps python3.pkgs);

  preBuild = lib.optionalString (rev != null) ''
    echo "__version__ = \"${rev}\"" > nix_alien/_version.py
    substituteInPlace {nix_alien,tests}/*.{py,nix} \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
  '';

  doCheck = !dev;

  nativeCheckInputs = with python3.pkgs; [
    pytestCheckHook
  ];

  meta = with lib; {
    description = "Run unpatched binaries on Nix/NixOS";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
