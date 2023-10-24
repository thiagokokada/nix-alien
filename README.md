# nix-alien

![nix-alien](./.github/nix-alien.jpg)

[![FlakeHub](https://img.shields.io/endpoint?url=https://flakehub.com/f/thiagokokada/nix-alien/badge)](https://flakehub.com/flake/thiagokokada/nix-alien)

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

## Quick start

If your binary is located in `~/myapp`, run:

```console
$ nix --extra-experimental-features "nix-command flakes" run github:thiagokokada/nix-alien -- ~/myapp
```
_Tip_: if you are trying to run an OpenGL binary (e.g.: `blender`) in non-NixOS
systems, you can wrap the command above in
[nixGL](https://github.com/guibou/nixGL):

```console
$ nix --extra-experimental-features "nix-command flakes" run --impure github:guibou/nixGL --override-input nixpkgs nixpkgs/nixos-unstable -- nix run github:thiagokokada/nix-alien -- blender
```

## Usage

Once `nix-alien` is installed in your system, all you need to do is run:

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
usage: nix-alien [-h] [--version] [-l LIBRARY] [-p PACKAGE] [-r] [-d PATH] [-P] [-E] [-s] [-f] program ...

positional arguments:
  program               Program to run
  ellipsis              Arguments to be passed to the program

options:
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
  -E, --edit            Edit 'default.nix' using $EDITOR (or 'nano' if unset)
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
```

### Usage without installing with Flakes

You can also run the scripts from this repo directly without clonning or
installing them, assuming you're using [a resonable up-to-date nix and enabled
experimental Flakes support](https://nixos.wiki/wiki/Flakes#Enable_flakes).

```console
$ nix run "github:thiagokokada/nix-alien#nix-alien" -- ~/myapp
$ nix run "github:thiagokokada/nix-alien#nix-alien-ld" -- ~/myapp
$ nix run "github:thiagokokada/nix-alien#nix-alien-find-libs" -- ~/myapp
```

Or if you don't have Flakes enabled but still wants to run it without
downloading it first:

```console
$ nix --extra-experimental-features "nix-command flakes" run "github:thiagokokada/nix-alien#nix-alien" -- ~/myapp
$ nix --extra-experimental-features "nix-command flakes" run "github:thiagokokada/nix-alien#nix-alien-ld" -- ~/myapp
$ nix --extra-experimental-features "nix-command flakes" run "github:thiagokokada/nix-alien#nix-alien-find-libs" -- ~/myapp
```

## NixOS Installation

You can add the following contents to a `/etc/nixos/nix-alien.nix` file:

``` nix
{ ... }:

let
  nix-alien-pkgs = import (
    builtins.fetchTarball "https://github.com/thiagokokada/nix-alien/tarball/master"
  ) { };
in
{
  environment.systemPackages = with nix-alien-pkgs; [
    nix-alien
  ];

  # Optional, but this is needed for `nix-alien-ld` command
  programs.nix-ld.enable = true;
}
```

And afterwards, add it to `imports` section on `/etc/nixos/configuration.nix`
file.

### NixOS installation with Flakes

> :warning: Overriding `nix-alien` inputs may cause mismatches between the
> `nix-index-database` and `nixpkgs`, causing possibly incorrect results, so it
> is unsupported.

If you're using NixOS with Flakes, you can do something similar to your NixOS
setup to install `nix-alien` on system `PATH`:

```nix
{
  description = "nix-alien-on-nixos";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.nix-alien.url = "github:thiagokokada/nix-alien";

  outputs = { self, nixpkgs, nix-alien }: {
      nixosConfigurations.nix-alien-desktop = nixpkgs.lib.nixosSystem rec {
        system = "x86_64-linux"; # or aarch64-linux
        specialArgs = { inherit self system; };
        modules = [
          ({ self, system, ... }: {
            environment.systemPackages = with self.inputs.nix-alien.packages.${system}; [
              nix-alien
            ];
            # Optional, needed for `nix-alien-ld`
            programs.nix-ld.enable = true;
          })
        ];
    };
  };
}
```

Alternatively, you can also use the included overlay. Keep in mind that the
overlay will use your current `nixpkgs` pin instead the one included in this
project `flake.lock` file.

This has the advantage of reducing the general size of your `/nix/store`,
however since the version of `nixpkgs` you currently have is not tested this may
cause issues.

```nix
{
  description = "nix-alien-on-nixos";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.nix-alien.url = "github:thiagokokada/nix-alien";

  outputs = { self, nixpkgs, nix-alien }: {
      nixosConfigurations.nix-alien-desktop = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux"; # or aarch64-linux
        specialArgs = { inherit self; };
        modules = [
          ({ self, ... }: {
            nixpkgs.overlays = [
              self.inputs.nix-alien.overlays.default
            ];
            environment.systemPackages = with pkgs; [
              nix-alien
            ];
            # Optional, needed for `nix-alien-ld`
            programs.nix-ld.enable = true;
          })
        ];
    };
  };
}
```

## Home-Manager Installation

You can add the following contents to your Home-Manager configuration file:

``` nix
{ ... }:

let
  nix-alien-pkgs = import (
    builtins.fetchTarball "https://github.com/thiagokokada/nix-alien/tarball/master"
  ) { };
in
{
  # ...
  home.packages = with nix-alien-pkgs; [
    nix-alien
  ];
}
```

### Home-Manager installation with Flakes

If you're using Home-Manager with Flakes, you can use:

```nix
{
  description = "nix-alien-on-home-manager";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.home-manager.url = "github:nix-community/home-manager";
  inputs.nix-alien.url = "github:thiagokokada/nix-alien";

  outputs = { self, nixpkgs, home-manager, nix-alien }:
    let
      system = "x86_64-linux"; # or aarch64-linux
      pkgs = import nixpkgs { inherit system; };
    in {
        homeConfigurations.nix-alien-home = home-manager.lib.homeManagerConfiguration rec {
          inherit pkgs;
          extraSpecialArgs = { inherit self system; };
          modules = [
            ({ self, system, ... }: {
              home.packages = with self.inputs.nix-alien.packages.${system}; [
                nix-alien
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

## Credits

- Inspired by [Lassulus/nix-autobahn](https://github.com/Lassulus/nix-autobahn)
- Thanks to [Mic92/nix-ld](https://github.com/Mic92/nix-ld),
  [Mic92/nix-index-database](https://github.com/Mic92/nix-index-database) and
  [bennofs/nix-index](https://github.com/bennofs/nix-index), since without them
  this project wouldn't be possible
