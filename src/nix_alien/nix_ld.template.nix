{ pkgs ? import
    (builtins.fetchTarball {
      name = "nixpkgs-unstable-@nixpkgsLastModifiedDate@";
      url = "https://github.com/NixOS/nixpkgs/archive/@nixpkgsRev@.tar.gz";
      sha256 = "@nixpkgsHash@";
    })
    { }
}:

let
  inherit (pkgs) lib stdenv;
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    ${__packages__}
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
in
pkgs.writeShellScriptBin "${__name__}" ''
  export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
  export NIX_LD='${NIX_LD}'
  ${__program__} "$@"
''
