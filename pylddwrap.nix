# TODO: upstream it to nixpkgs
{ lib
, coreutils
, glibc
, python3
, fetchFromGitHub
}:

python3.pkgs.buildPythonPackage {
  pname = "pylddwrap";
  version = "unstable-2022-10-13";

  src = fetchFromGitHub {
    owner = "Parquery";
    repo = "pylddwrap";
    rev = "4022994d5557a421ec344a074c53ba58a0241e43";
    hash = "sha256-aFpkAWyFEW/tFPP00nPH+PNqGCuv2y2MQwxNYuIcenY=";
  };

  postPatch = ''
    substituteInPlace lddwrap/__init__.py \
      --replace '/usr/bin/env' '${coreutils}/bin/env'
  '';

  propagatedBuildInputs = with python3.pkgs; [
    icontract
    glibc.bin
  ];

  meta = with lib; {
    description = "Python wrapper around ldd *nix utility to determine shared libraries of a program";
    homepage = "https://github.com/Parquery/pylddwrap";
    license = licenses.mit;
  };
}
