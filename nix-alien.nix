{ lib
, callPackage
, python3
, fzf
, rev ? null
, dev ? false
, ci ? false
}:

assert dev -> (ci == false);
let
  pylddwrap = callPackage ./pylddwrap.nix { };
  version = if (rev != null) then rev else "dev";
in
python3.pkgs.buildPythonApplication {
  inherit version;

  pname = "nix-alien";
  format = "pyproject";

  src = ./.;

  propagatedBuildInputs = with python3.pkgs; [
    pyfzf
    pylddwrap
    setuptools
  ];

  preBuild = lib.optionalString (rev != null) ''
    echo "__version__ = \"${rev}\"" > nix_alien/_version.py
  '';

  doCheck = !dev;

  checkInputs = with python3.pkgs; [
    fzf
    pytestCheckHook
  ]
  ++ lib.optionals ci [
    black
    mypy
  ];

  preCheck = lib.optionalString ci ''
    black --check ./nix_alien
    mypy --ignore-missing-imports ./nix_alien
  '';

  meta = with lib; {
    description = "Run unpatched binaries on Nix/NixOS";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
