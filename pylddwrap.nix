# TODO: remove after https://github.com/NixOS/nixpkgs/pull/199341 is merged
{ lib
, buildPythonPackage
, coreutils
, fetchFromGitHub
, icontract
, pytestCheckHook
, pythonOlder
, typing-extensions
}:

buildPythonPackage rec {
  pname = "pylddwrap";
  version = "unstable-2022-10-13";
  format = "setuptools";
  disabled = pythonOlder "3.6";

  src = fetchFromGitHub {
    owner = "Parquery";
    repo = pname;
    rev = "4022994d5557a421ec344a074c53ba58a0241e43";
    hash = "sha256-aFpkAWyFEW/tFPP00nPH+PNqGCuv2y2MQwxNYuIcenY=";
  };

  postPatch = ''
    substituteInPlace lddwrap/__init__.py \
      --replace '/usr/bin/env' '${coreutils}/bin/env'
  '';

  # Upstream adds some plain text files direct to the package's root directory
  # https://github.com/Parquery/pylddwrap/blob/master/setup.py#L71
  postInstall = ''
    rm -f $out/{LICENSE,README.rst,requirements.txt}
  '';

  propagatedBuildInputs = [
    icontract
    typing-extensions
  ];

  checkInputs = [ pytestCheckHook ];

  pythonImportsCheck = [ "lddwrap" ];

  meta = with lib; {
    description = "Python wrapper around ldd *nix utility to determine shared libraries of a program";
    homepage = "https://github.com/Parquery/pylddwrap";
    changelog = "https://github.com/Parquery/pylddwrap/blob/v${version}/CHANGELOG.rst";
    license = licenses.mit;
    maintainers = with maintainers; [ thiagokokada ];
  };
}
