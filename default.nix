{ nixpkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/f112b512e1710da6c8beb8e541a8ad9fcd81e6e6.tar.gz") { }
, poetry2nix ? import (fetchTarball "https://github.com/nix-community/poetry2nix/archive/refs/tags/1.21.0.tar.gz") { pkgs = nixpkgs; poetry = nixpkgs.poetry; }
}:

poetry2nix.mkPoetryApplication {
  projectDir = ./.;
}
