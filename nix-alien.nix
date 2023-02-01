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
    pytestCheckHook
  ];

  preCheck = ''
    export PATH="${lib.makeBinPath [ fzf ]}:$PATH"
  ''
  + lib.optionalString ci ''
    export PATH="${with python3.pkgs; lib.makeBinPath [ black mypy pylint ]}:$PATH"
    export PYLINTHOME="$(mktemp -d)"
    black --check ./nix_alien
    mypy --ignore-missing-imports ./nix_alien
    pylint ./nix_alien -d=C0116,C0114,R0801,R0913
  '';

  meta = with lib; {
    description = "Run unpatched binaries on Nix/NixOS";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
