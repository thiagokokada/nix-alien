# nix-alien

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

To avoid the slow startup of `nix-index`, you can also download a pre-computed
index from [`nix-index-database`](https://github.com/Mic92/nix-index-database):

``` sh
$ nix run "github:thiagokokada/nix-alien#nix-index-update"
```

## Limitations

Binaries loading shared libraries dynamically (e.g.: with `dlopen`) will
probably not work with this script. However, this script can still be useful to
create an initial `default.nix` or `shell.nix`, that can be populated later with
the runtime dependencies of the program.

## Technical Description

This simple Python program allows you to download ELF binaries and use them
right away! This is achieved by enumerating the shared library dependencies from
the ELF header and then searching for the equivalent library in `nixpkgs`. This
is done by querying `nix-locate` locally.

To be able to use `nix-locate`, first, the index has to be build. This is done
by running `nix-index` and waiting 10-15 minutes. To speed-up this process,
this repo also includes `nix-index-update` script, that downloads the index from
[`nix-index-database`](https://github.com/Mic92/nix-index-database).

## Credits

Inspired by [nix-autobahn](https://github.com/Lassulus/nix-autobahn). The
original version is written in shell script, this one is written in Python and
also brings some improvements.
