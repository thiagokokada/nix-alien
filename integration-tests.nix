{ self ? (import ./compat.nix).flake
}:

let
  pkgs = import self.inputs.nixpkgs {
    system = "x86_64-linux";
    overlays = [ self.overlays.default ];
  };
  inherit (pkgs) lib coreutils gnugrep nix-alien nix shunit2;
  babashkaVersion = "1.3.185";
  babashka = pkgs.fetchzip {
    url = "https://github.com/babashka/babashka/releases/download/v${babashkaVersion}/babashka-${babashkaVersion}-linux-amd64.tar.gz";
    hash = "sha256-2WzGw0GxJpL3owiSf24moZvAeQ8TKFSul1PRvKS3OWI=";
  };
  cleanEnv = ''env -i PATH="$PATH" HOME="$HOME"'';
in
{
  it = pkgs.writeShellScriptBin "nix-alien-it" ''
    export PATH="${lib.makeBinPath [ coreutils gnugrep nix-alien nix ]}"
    export HOME="$(mktemp -d)"
    . /etc/os-release

    testNixAlien() {
      ${cleanEnv} nix-alien -c zlib ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    }

    testNixAlienFlake() {
      ${cleanEnv} nix-alien -c zlib --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    }

    testNixAlienFindLibs() {
      ${cleanEnv} nix-alien-find-libs -c zlib ${babashka}/bb | grep -F "zlib.out"
    }

    # The tests below will fail in a NixOS system without NIX_LD setup, so we
    # just test evaluation by checking if the error is the expect one (e.g.: lack
    # of libs instead of nix eval errors).
    # On non-NixOS systems (like GitHub Actions) this will work because babashka
    # will just re-use the system libs (and almost every system contains zlib
    # installed).
    testNixAlienLd() {
      if [[ "$NAME" == "NixOS" ]] && [[ -z "$NIX_LD" ]]; then
        echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
        ${cleanEnv} nix-alien-ld -c zlib ${babashka}/bb -- --version 2>&1 | grep -F "Could not start dynamically linked executable"
      else
        ${cleanEnv} nix-alien-ld -c zlib ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
      fi
    }

    testNixAlienLdFlake() {
      if [[ "$NAME" == "NixOS" ]] && [[ -z "$NIX_LD" ]]; then
        echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
        ${cleanEnv} nix-alien-ld -c zlib --flake ${babashka}/bb -- --version 2>&1 | grep -F "Could not start dynamically linked executable"
      else
        ${cleanEnv} nix-alien-ld -c zlib --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
      fi
    }

    . ${shunit2}/bin/shunit2
  '';
}
