{ lib
, stdenvNoCC
, coreutils
, substituteAll
, system
, wget
}:

stdenvNoCC.mkDerivation {
  pname = "nix-index-update";
  version = "0.0.1";

  src = substituteAll {
    src = ./nix-index-update.sh;
    isExecutable = true;
    inherit coreutils wget system;
  };

  dontUnpack = true;

  installPhase = ''
    runHook preInstall

    install -Dm755 "$src" "$out/bin/nix-index-update"

    runHook postInstall
  '';

  meta = with lib; {
    description = "Update nix-index cache using https://github.com/Mic92/nix-index-database";
    homepage = "https://github.com/thiagokokada/nix-alien";
    license = licenses.mit;
  };
}
