{
  self ? (import ./compat.nix).flake,
}:

let
  pkgs = import self.inputs.nixpkgs {
    system = "x86_64-linux";
    overlays = [ self.overlays.default ];
  };
  babashkaVersion = "1.12.218";
  babashka = pkgs.fetchzip {
    url = "https://github.com/babashka/babashka/releases/download/v${babashkaVersion}/babashka-${babashkaVersion}-linux-amd64.tar.gz";
    hash = "sha256-PvzzMjuPGzvjaXQGVKi4IE1/MTUuIETb5FyCsqZ77Po=";
  };
in
{
  it = pkgs.testers.runNixOSTest {
    name = "nix-alien";

    nodes.machine =
      { pkgs, ... }:
      {
        environment.systemPackages = with pkgs; [
          nix-alien
        ];

        programs.nix-ld.enable = true;

        nix = {
          nixPath = [ "${self.inputs.nixpkgs}" ];
          # settings = {
          #   substituters = lib.mkForce [ ];
          #   hashed-mirrors = null;
          #   connect-timeout = 1;
          # };
        };

        # FIXME: the tests are impure, need to run with `--option sandbox false`
        networking.useDHCP = true;

        system = {
          # includeBuildDependencies = true;
          extraDependencies = with pkgs; [
            zlib
          ];
        };

        virtualisation = {
          cores = 2;
          memorySize = 2048;
          diskSize = 10240;
        };
      };

    testScript = # python
      ''
        start_all()

        machine.wait_for_unit("multi-user.target")

        # FIXME: this may be regression in nixpkgs, but it is not our job to fix it.
        # > machine # /nix/store/.../bb: error while loading shared libraries: /nix/store/.../lib/libc.so: invalid ELF header
        # machine.succeed("nix-alien -c zlib ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        # machine.succeed("nix-alien -c zlib --flake ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        # machine.succeed("nix-alien-ld -c zlib ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        # machine.succeed("nix-alien-ld -c zlib --flake ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        machine.succeed("nix-alien-find-libs -c zlib ${babashka}/bb | grep -F 'zlib.out'")
      '';
  };
}
