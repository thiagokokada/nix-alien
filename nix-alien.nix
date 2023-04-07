{ lib
, fzf
, nix-index
, python3
, rev ? null
, dev ? false
, ci ? false
}:

assert dev -> !ci;
let
  version = if (rev != null) then rev else "dev";
  deps = with builtins;
    filter (s: isString s && s != "")
      (split "\n"
        (readFile ./requirements.txt));
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
  '';

  doCheck = !dev;

  nativeCheckInputs = with python3.pkgs; [
    pytestCheckHook
  ] ++ lib.optionals ci [
    black
    mypy
    pylint
  ];

  preCheck = lib.optionalString ci ''
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
