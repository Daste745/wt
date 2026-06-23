{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      systems,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      eachSystem =
        f: nixpkgs.lib.genAttrs (import systems) (system: f (import nixpkgs { inherit system; }));
    in
    {
      devShells = eachSystem (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python314
            python314Packages.uv

            # For examples
            nodejs
            pnpm
          ];
          shellHook = ''
            uv sync --frozen --no-install-project --group dev
          '';
        };
      });
      packages = eachSystem (pkgs: {
        wt = pkgs.callPackage ./package.nix {
          inherit uv2nix pyproject-nix pyproject-build-systems;
          python = pkgs.python314;
        };
      });
    };
}
