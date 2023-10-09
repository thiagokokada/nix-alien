{ writeShellApplication
, coreutils
, system
, wget
}:

writeShellApplication {
  name = "nix-index-update";

  runtimeInputs = [
    coreutils
    wget
  ];

  text = ''
    readonly filename="index-${system}"
    readonly dest_dir="$HOME/.cache/nix-index"

    mkdir -p "$dest_dir"
    pushd "$dest_dir" >/dev/null
    trap "popd >/dev/null" EXIT

    # -N will only download a new version if there is an update.
    wget -q -N "https://github.com/Mic92/nix-index-database/releases/latest/download/$filename"
    ln -f "$filename" files

    echo "Done!"
  '';
}
