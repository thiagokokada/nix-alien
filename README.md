# nix-alien

![nix-alien](./.github/nix-alien.jpg)

[![ci](https://github.com/thiagokokada/nix-alien/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagokokada/nix-alien/actions/workflows/ci.yml)

## Introduction

You are running nix/NixOS and have ever encountered the following problem?

```sh
$ ./bb
bash: ./bb: No such file or directory
```

Fear not, now there is `nix-alien` which will download necessary dependencies
for you.

```sh
$ ./nix-alien bb            --> Run the binary inside a FHS shell with all needed shared dependencies to execute the binary
$ ./nix-alien-ld bb         --> Spawns you inside a shell with NIX_LD_LIBRARY_PATH set to the needed dependencies, to be used with nix-ld
$ ./nix-alien-find-libs bb  --> Lists all libs needed for the binary
```

## Usage (Flakes)

Assuming you have `nix` already installed:

```sh
$ nix-shell -p nixUnstable nix-index
$ nix-index # this will take a long time
$ nix run --experimental-features 'nix-command flakes' "github:thiagokokada/nix-alien" -- ~/myapp
```

This will run `nix-alien` on `~/myapp` binary with a `FHSUserEnv` including all
shared library dependencies. The resulting `default.nix` file will be saved to
`$XDG_CACHE_HOME/nix-alien/<path-uuid>/default.nix`, making the next evaluation
faster. You can also pass `--recreate` flag to force the recreation of
`default.nix` file

You can edit your `/etc/nix/nix.conf` or `~/.config/nix/nix.conf` file and
add the following line to avoid having to pass `--experimental-features` flag
every time:

```ini
experimental-features = nix-command flakes
```

From here on this guide will assume the above configuration is done for brevity.

To pass arguments to the app:

```sh
$ nix run "github:thiagokokada/nix-alien" -- ~/myapp -- --help
```

In case you're using [`nix-ld`](https://github.com/Mic92/nix-ld), there is also
`nix-alien-ld`:

``` sh
$ nix run "github:thiagokokada/nix-alien#nix-alien-ld" -- ~/myapp 
```

This will spawn a `mkShell` instead with `NIX_LD_LIBRARY_PATH` and `NIX_LD`
setup. The resulting `shell.nix` file will be saved to
`$XDG_CACHE_HOME/nix-alien/<path-uuid>/shell.nix`, making the next evaluation
faster. You can also pass `--recreate` flag to force the recreation of
`shell.nix` file

If you want to use the `fzf` based menu to find the libraries for scripting
purposes, you can run:

``` sh
$ nix run "github:thiagokokada/nix-alien#nix-alien-find-libs" -- ~/myapp 
```

This will print the found libraries on the `stdout`. The informational messages
are printed to `stderr`, so you can easily redirect them to `/dev/null` if
needed.

To avoid the slow startup of `nix-index`, you can also download a pre-computed
index from [`nix-index-database`](https://github.com/Mic92/nix-index-database):

``` sh
$ nix run "github:thiagokokada/nix-alien#nix-index-update"
```
## Usage (non-Flakes)

``` sh
$ $(nix-build default.nix --no-out-link)/bin/nix-alien ~/myapp -- --arg foo
$ $(nix-build default.nix --no-out-link)/bin/nix-alien-ld ~/myapp
$ $(nix-build default.nix --no-out-link)/bin/nix-alien-find-libs ~/myapp
$ $(nix-build nix-index-update.nix --no-out-link)/bin/nix-index-update
```

## Limitations

Binaries loading shared libraries dynamically (e.g.: with `dlopen`) will
probably not work with this script. However, this script can still be useful to
create an initial `default.nix` or `shell.nix`, that can be populated later with
the runtime dependencies of the program.

## Technical Description

This is achieved by enumerating the shared library dependencies from the ELF
header using `ldd` (actually,
[`pylddwrap`](https://github.com/Parquery/pylddwrap)) and then searching for the
equivalent library in `nixpkgs`. This is done by querying `nix-locate` locally.
To solve possible conflicts, human intervation is needed, but thanks to
[`fzf`](https://github.com/junegunn/fzf) and
[`pyfzf`](https://github.com/nk412/pyfzf) this is made easy by showing an
interactive list.

To be able to use `nix-locate`, first, the index has to be build. This is done
by running `nix-index` and waiting 10-15 minutes. To speed-up this process, this
repo also includes `nix-index-update` script, that downloads the index from
[`nix-index-database`](https://github.com/Mic92/nix-index-database).

## Credits

- Inspired by [Lassulus/nix-autobahn](https://github.com/Lassulus/nix-autobahn)
- Thanks to [Mic92/nix-ld](https://github.com/Mic92/nix-ld) and
  [bennofs/nix-index](https://github.com/bennofs/nix-index), since without them
  this project wouldn't be possible
