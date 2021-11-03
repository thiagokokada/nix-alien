#!/usr/bin/env bash

set -euo pipefail

readonly filename="index-@system@"
readonly dest_dir="$HOME/.cache/nix-index"

"@coreutils@/bin/mkdir" -p "$dest_dir"
pushd "$dest_dir" >/dev/null
trap "popd >/dev/null" EXIT

# -N will only download a new version if there is an update.
"@wget@/bin/wget" -q -N "https://github.com/Mic92/nix-index-database/releases/latest/download/$filename"
"@coreutils@/bin/ln" -f "$filename" files

echo "Done!"
