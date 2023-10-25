{ self ? (import ./compat.nix).flake
}:

let
  pkgs = import self.inputs.nixpkgs {
    system = "x86_64-linux";
    overlays = [ self.overlays.default ];
  };
  inherit (pkgs) lib nix-alien gnugrep;
  babashkaVersion = "1.3.185";
  babashka = pkgs.fetchzip {
    url = "https://github.com/babashka/babashka/releases/download/v${babashkaVersion}/babashka-${babashkaVersion}-linux-amd64.tar.gz";
    hash = "sha256-2WzGw0GxJpL3owiSf24moZvAeQ8TKFSul1PRvKS3OWI=";
  };
  setup = ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    . /etc/os-release
  '';
  reportResult = ''
    if [[ "$?" == 0 ]]; then
      echo "[TEST RESULT] Success!"
    else
      echo "[TEST RESULT] Failure!"
    fi
  '';
in
{
  nix-alien = pkgs.writeShellScriptBin "nix-alien-it" ''
    ${setup}
    nix-alien -c zlib.out ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    ${reportResult}
  '';

  nix-alien-flake = pkgs.writeShellScriptBin "nix-alien-flake-it" ''
    ${setup}
    nix-alien -c zlib.out --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    ${reportResult}
  '';

  nix-alien-find-libs = pkgs.writeShellScriptBin "nix-alien-find-libs-it" ''
    ${setup}
    nix-alien-find-libs -c zlib.out ${babashka}/bb | grep -F "zlib.out"
    ${reportResult}
  '';

  # The tests below will fail in a NixOS system without NIX_LD setup, so we
  # just test evaluation by checking if the error is the expect one (e.g.: lack
  # of libs instead of nix eval errors).
  # On non-NixOS systems (like GitHub Actions) this will work because babashka
  # will just re-use the system libs (and almost every system contains zlib
  # installed).
  nix-alien-ld = pkgs.writeShellScriptBin "nix-alien-ld-it" ''
    ${setup}
    if [[ "$NAME" == "NixOS" ]] && [[ -z "$NIX_LD" ]]; then
      echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
      nix-alien-ld -c zlib.out ${babashka}/bb -- --version 2>&1 | grep -F "required file not found"
    else
      nix-alien-ld -c zlib.out ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    fi
    ${reportResult}
  '';

  nix-alien-ld-flake = pkgs.writeShellScriptBin "nix-alien-ld-flake-it" ''
    ${setup}
    if [[ "$NAME" == "NixOS" ]] && [[ -z "$NIX_LD" ]]; then
      echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
      nix-alien-ld -c zlib.out --flake ${babashka}/bb -- --version 2>&1 | grep -F "required file not found"
    else
      nix-alien-ld -c zlib.out --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    fi
    ${reportResult}
  '';
}
