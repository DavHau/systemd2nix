{ pkgs ? import <nixpkgs> { } }:
# very lazy packaging
with pkgs;
writeScriptBin "systemd2nix" ''
  #!/usr/bin/env bash
  ${python3}/bin/python ${./systemd2nix.py} "$@"
''
