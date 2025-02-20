{
  self ? (import ./compat.nix).flake,
}:

let
  pkgs = import self.inputs.nixpkgs {
    system = "x86_64-linux";
    overlays = [ self.overlays.default ];
  };
  babashkaVersion = "1.3.185";
  babashka = pkgs.fetchzip {
    url = "https://github.com/babashka/babashka/releases/download/v${babashkaVersion}/babashka-${babashkaVersion}-linux-amd64.tar.gz";
    hash = "sha256-2WzGw0GxJpL3owiSf24moZvAeQ8TKFSul1PRvKS3OWI=";
  };
in
{
  it = pkgs.testers.runNixOSTest {
    name = "nix-alien";

    nodes.machine =
      { pkgs, lib, ... }:
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

        machine.succeed("nix-alien -c zlib ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        machine.succeed("nix-alien -c zlib --flake ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        machine.succeed("nix-alien-ld -c zlib ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        machine.succeed("nix-alien-ld -c zlib --flake ${babashka}/bb -- --version | grep -F 'babashka v${babashkaVersion}'")
        machine.succeed("nix-alien-find-libs -c zlib ${babashka}/bb | grep -F 'zlib.out'")
      '';
  };
}
