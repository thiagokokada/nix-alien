{ lib
, fzf
, nix-index
, nixpkgs-src
, python3
, ruff
, rev ? null
, dev ? false
, ci ? false
}:

assert dev -> !ci;
let
  version = if (rev != null) then rev else "dev";
  deps = (lib.importTOML ./pyproject.toml).project.dependencies;
in
python3.pkgs.buildPythonApplication {
  pname = "nix-alien";
  format = "pyproject";
  inherit version;

  src = ./.;

  nativeBuildInputs = [ fzf ];

  propagatedBuildInputs = with python3.pkgs; [
    nix-index
    setuptools
  ] ++ (lib.attrVals deps python3.pkgs);

  preBuild = lib.optionalString (rev != null) ''
    echo "__version__ = \"${rev}\"" > nix_alien/_version.py
    substituteInPlace nix_alien/fhs_env.template.nix \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
    substituteInPlace tests/test_fhs_env.py \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
    substituteInPlace nix_alien/nix_ld.template.nix \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
    substituteInPlace tests/test_nix_ld.py \
      --subst-var-by nixpkgsLastModifiedDate ${nixpkgs-src.lastModifiedDate} \
      --subst-var-by nixpkgsRev ${nixpkgs-src.rev} \
      --subst-var-by nixpkgsHash ${nixpkgs-src.narHash}
  '';

  doCheck = !dev;

  nativeCheckInputs = with python3.pkgs; [
    pytestCheckHook
  ] ++ lib.optionals ci [
    black
    mypy
    ruff
  ];

  preCheck = lib.optionalString ci ''
    export PYLINTHOME="$(mktemp -d)"
    black --check ./nix_alien
    mypy --ignore-missing-imports ./nix_alien
    ruff check ./nix_alien
  '';

  meta = with lib; {
    description = "Run unpatched binaries on Nix/NixOS";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
