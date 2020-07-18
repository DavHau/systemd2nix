with import <nixpkgs> {};

# very lazy packaging
writeScriptBin "systemd2nix" ''
  #!/usr/bin/env bash
  ${python3}/bin/python ${./systemd2nix.py} "$@"
''
