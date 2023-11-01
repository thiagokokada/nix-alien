__version__ = "@version@"
__nix_index_database_rev__ = "@nixIndexDatabaseRev@"
# They should always be the same unless the user overrides them
__nixpkgs_rev__ = "@nixpkgsRev@"
__nixpkgs_build_rev__ = "@nixpkgsBuildRev@"

if __nixpkgs_rev__ != __nixpkgs_build_rev__:
    nixpkgs_build_rev = f"nixpkgs-build={__nixpkgs_build_rev__}"
else:
    nixpkgs_build_rev = ""

version = f"""
version={__version__}
nix-index-database={__nix_index_database_rev__}
nixpkgs={__nixpkgs_rev__}
{nixpkgs_build_rev}
"""
