# nix-alien

![nix-alien](./.github/nix-alien.jpg)

[![ci](https://github.com/thiagokokada/nix-alien/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagokokada/nix-alien/actions/workflows/ci.yml)

## Introduction

You are running nix/NixOS and have ever encountered the following problem?

```console
$ ./myapp
bash: ./myapp: No such file or directory
```

Fear not, now there is `nix-alien` which will download necessary dependencies
for you.

```console
$ nix-alien myapp            # Run the binary inside a FHS shell with all needed shared dependencies to execute the binary
$ nix-alien-ld myapp         # Spawns you inside a shell with NIX_LD_LIBRARY_PATH set to the needed dependencies, to be used with nix-ld
$ nix-alien-find-libs myapp  # Lists all libs needed for the binary
```

## Usage

Assuming you have `nix-alien` and `nix-index-update` installed, start by
running:

```console
$ nix-index-update
```

This will avoid the slow startup of `nix-locate` by downloading it from a
pre-computed index from
[`nix-index-database`](https://github.com/Mic92/nix-index-database). You can
also run `nix-index` command to compute the index locally (this will take a
while).

Afterwards, start by running:

```console
$ nix-alien ~/myapp
```

This will run `nix-alien` on `~/myapp` binary with a `FHSUserEnv` including all
shared library dependencies. The resulting `default.nix` file will be saved to
`$XDG_CACHE_HOME/nix-alien/<path-uuid>/fhs-env/default.nix`, making the next
evaluation faster. The cache is based on the binary absolute path. You can also
pass `--recreate` flag to force the recreation of `default.nix` file, and
`--destination` to change where `default.nix` file will be saved.

To pass arguments to the app:

```console
$ nix-alien ~/myapp -- --foo bar
```

In case you're using [`nix-ld`](https://github.com/Mic92/nix-ld), there is also
`nix-alien-ld`:

```console
$ nix-alien-ld -- ~/myapp 
```

This will spawn a wrapped binary with `NIX_LD_LIBRARY_PATH` and `NIX_LD` setup.
The resulting `default.nix` file will be saved to
`$XDG_CACHE_HOME/nix-alien/<path-uuid>/nix-ld/default.nix`, making the next
evaluation faster. The cache is based on the binary absolute path. You can also
pass `--recreate` flag to force the recreation of `default.nix` file, and
`--destination` to change where `default.nix` file will be saved.

To pass arguments to the app:

```console
$ nix-alien-ld ~/myapp -- --foo bar
```

If you want to use the `fzf` based menu to find the libraries for scripting
purposes, you can run:

```console
$ nix-alien-find-libs ~/myapp 
```

This will print the found libraries on the `stdout`. The informational messages
are printed to `stderr`, so you can easily redirect them to `/dev/null` if
needed. You can also use `--json` flag to print the result as a JSON instead.

There are also some other options, check them using `--help` flag on each
program. Example for `nix-alien`:

```console
usage: nix-alien [-h] [--version] [-l LIBRARY] [-p PACKAGE] [-r] [-d PATH] [-P] [-s] [-f] program ...

positional arguments:
  program               Program to run
  ellipsis              Arguments to be passed to the program

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -l LIBRARY, --additional-libs LIBRARY
                        Additional library to search. May be passed multiple times
  -p PACKAGE, --additional-packages PACKAGE
                        Additional package to add. May be passed multiple times
  -r, --recreate        Recreate 'default.nix' file if exists
  -d PATH, --destination PATH
                        Path where 'default.nix' file will be created
  -P, --print-destination
                        Print where 'default.nix' file is located and exit
  -s, --silent          Silence informational messages
  -f, --flake           Create and use 'flake.nix' file instead (experimental)
```

### Usage without installing

You can also run the scripts from this repo on any Nix/NixOS setup. However, in
this case you will need to have a copy of this repository first:

```console
$ git clone https://github.com/thiagokokada/nix-alien && cd nix-alien
$ $(nix-build nix-alien.nix --no-out-link)/bin/nix-alien ~/myapp
$ $(nix-build nix-alien.nix --no-out-link)/bin/nix-alien-ld ~/myapp
$ $(nix-build nix-alien.nix --no-out-link)/bin/nix-alien-find-libs ~/myapp
$ $(nix-build nix-index-update.nix --no-out-link)/bin/nix-index-update
```

### Usage without installing with Flakes

You can also run the scripts from this repo directly without clonning or
installing them, assuming you're using [a resonable up-to-date nix and enabled
experimental Flakes support](https://nixos.wiki/wiki/Flakes#Enable_flakes).

```console
$ nix run "github:thiagokokada/nix-alien#nix-alien" -- ~/myapp
$ nix run "github:thiagokokada/nix-alien#nix-alien-ld" -- ~/myapp
$ nix run "github:thiagokokada/nix-alien#nix-alien-find-libs" -- ~/myapp
$ nix run "github:thiagokokada/nix-alien#nix-index-update"
```

## NixOS Installation

You can add the following contents to a `/etc/nixos/nix-alien.nix` file:

``` nix
{ pkgs, ... }:

let
  nix-alien-pkgs = import (
    fetchTarball "https://github.com/thiagokokada/nix-alien/tarball/master"
  ) { };
in
{
  # Optional, but this is needed for `nix-alien-ld` command
  # See https://github.com/Mic92/nix-ld#installation for how to setup `nix-ld`
  # channel
  imports = [
    <nix-ld/modules/nix-ld.nix>
  ];

  environment.systemPackages = with nix-alien-pkgs; [
    nix-alien
    nix-index-update
    pkgs.nix-index # not necessary, but recommended
  ];
}
```

And afterwards, add it to `imports` section on `/etc/nixos/configuration.nix`
file.

### NixOS installation with Flakes

If you're using NixOS with Flakes, you can do something similar to your NixOS
setup to install `nix-alien` on system `PATH`:

```nix
{
  description = "nix-alien-on-nixos";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.nix-alien.url = "github:thiagokokada/nix-alien";
  inputs.nix-ld.url = "github:Mic92/nix-ld/main";

  outputs = { self, nixpkgs, nix-alien }: {
      nixosConfigurations.nix-alien-desktop = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit self; };
      modules = [
        ({ self, ... }: {
          nixpkgs.overlays = [
            self.inputs.nix-alien.overlays.default
          ];
	  imports = [
            # Optional, but this is needed for `nix-alien-ld` command
            self.inputs.nix-ld.nixosModules.nix-ld
          ];
          environment.systemPackages = with pkgs; [
            nix-alien
            nix-index # not necessary, but recommended
            nix-index-update
          ];
        })
      ];
    };
  };
}
```

## Development

On non-Flakes system, you can use `nix-shell` to start a development shell.

On Flakes enabled system, you can use `nix develop` instead.

If you have [`nix-direnv`](https://github.com/nix-community/nix-direnv/)
installed, there is a `.envrc` file configured to start the Flakes enabled setup
automatically. Just run `direnv allow` inside this repo.

## Limitations

Binaries loading shared libraries dynamically (e.g.: with `dlopen`) will
probably not work with this script. However, this can be workarounded using
either `--additional-libs/-l` or `--additional-packages/-p` flag. The first one
can be used as:

``` console
$ nix-alien -l libGL.so.1 -l libz.so.1 ~/myapp
```

And this will be searched using `nix-locate` in a similar way as the other
libraries found in the binary. The second one can be used as:

``` console
$ nix-alien -p libGL -p zlib ~/myapp
```

To direct add the package to `default.nix` file. Warning: there is no
validation, so you can receive an `undefied variable` error in case of
an inexistent package.

## Technical Description

This is achieved by enumerating the shared library dependencies from the ELF
header using `ldd` (actually,
[`pylddwrap`](https://github.com/Parquery/pylddwrap)) and then searching for the
equivalent library in `nixpkgs`. This is done by querying `nix-locate` locally.
To solve possible conflicts, human intervation is needed, but thanks to
[`fzf`](https://github.com/junegunn/fzf) and
[`pyfzf`](https://github.com/nk412/pyfzf) this is made easy by
showing an interactive list.

To be able to use `nix-locate`, first, the index has to be build. This is done
by running `nix-index` and waiting 10-15 minutes. To speed-up this process, this
repo also includes `nix-index-update` script, that downloads the index from
[`nix-index-database`](https://github.com/Mic92/nix-index-database).

## Credits

- Inspired by [Lassulus/nix-autobahn](https://github.com/Lassulus/nix-autobahn)
- Thanks to [Mic92/nix-ld](https://github.com/Mic92/nix-ld) and
  [bennofs/nix-index](https://github.com/bennofs/nix-index), since without them
  this project wouldn't be possible
