{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = { nixpkgs, ... }@inputs:
    with inputs;
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages.systemd2nix = pkgs.callPackage ./default.nix { };
        defaultPackage = packages.systemd2nix;
      });
}
