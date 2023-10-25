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
in
{
  nix-alien = pkgs.writeShellScriptBin "nix-alien-it" ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    nix-alien -c zlib.out ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
  '';

  nix-alien-flake = pkgs.writeShellScriptBin "nix-alien-flake-it" ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    nix-alien -c zlib.out --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
  '';

  nix-alien-find-libs = pkgs.writeShellScriptBin "nix-alien-find-libs-it" ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    nix-alien-find-libs -c zlib.out ${babashka}/bb | grep -F "zlib.out"
  '';

  # Without NIX_LD configured we will just test eval (e.g.: if the
  # `default.nix` file was generated correctly)
  nix-alien-ld = pkgs.writeShellScriptBin "nix-alien-ld-it" ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    if [[ -z "$NIX_LD" ]]; then
      echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
      nix-alien-ld -c zlib.out ${babashka}/bb -- --version 2>&1 | grep -F "required file not found"
    else
      nix-alien-ld -c zlib.out ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    fi
  '';

  nix-alien-ld-flake = pkgs.writeShellScriptBin "nix-alien-ld-flake-it" ''
    export PATH="${lib.makeBinPath [ nix-alien gnugrep ]}:$PATH"
    export HOME="$(mktemp -d)"
    if [[ -z "$NIX_LD" ]]; then
      echo "[WARN] NIX_LD not setup! Will only test nix evaluation."
      nix-alien-ld -c zlib.out --flake ${babashka}/bb -- --version 2>&1 | grep -F "required file not found"
    else
      nix-alien-ld -c zlib.out --flake ${babashka}/bb -- --version | grep -F "babashka v${babashkaVersion}"
    fi
  '';
}
