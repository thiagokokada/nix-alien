__version__ = "@version@"
__nix_index_database_rev__ = "@nixIndexDatabaseRev@"
__nixpkgs_rev__ = "@nixpkgsRev@"

version = f"""
version={__version__}
nix-index-database={__nix_index_database_rev__}
nixpkgs={__nixpkgs_rev__}
"""
