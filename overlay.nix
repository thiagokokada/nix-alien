{
  final,
  prev,
  self ? (import ./compat.nix).flake,
}:

import ./default.nix {
  inherit self;
  pkgs = prev;
}
