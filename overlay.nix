{ final
, prev
, self ? { }
}:

import ./default.nix {
  inherit self;
  pkgs = prev;
}
