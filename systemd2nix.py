#!/usr/bin/env python3

import json
import re
import sys
from argparse import ArgumentParser
from configparser import ConfigParser


class Keys:
    
    list_of_strings = [
        'after',
        'before',
        'bindsTo',
        'conflicts',
        'documentation',
        'partOf',
        'requiredBy',
        'requires',
        'requisite',
        'wantedBy',
        'wants',
    ]

    rest = [
        'description',
        'onFailure',
        'postStart',
        'postStop',
        'preStart',
        'preStop',
        'reload',
        'reloadIfChanged',
        'restartIfChanged',
        'restartTriggers',
        'startAt',
        'startLimitIntervalSec',
        'stopIfChanged',
    ]

    all = list_of_strings + rest


class MyParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    def optionxform(self, optionstr: str) -> str:
        return optionstr


def key2nix(key: str):
    return key[0].lower() + key[1:]


def parse_environment(env: str) -> dict:
    separated = env.strip().split(' ')
    return dict(map(lambda s: s.split('='), separated))


def format_config(conf: dict) -> dict:
    new_conf = dict(environment={})
    if 'Install' in conf:
        for key, val in conf["Install"].items():
            key = key2nix(key)
            new_conf[key] = val
    if "Service" in conf:
        if "Environment" in conf['Service']:
            new_conf['environment'] = parse_environment(conf['Service']['Environment'])
            del conf['Service']['Environment']
        new_conf['serviceConfig'] = conf['Service']
    if "Unit" in conf:
        for key, val in conf['Unit'].items():
            key = key2nix(key)
            if key in Keys.all:
                new_conf[key] = val
            else:
                if 'unitConfig' not in conf:
                    new_conf['unitConfig'] = {}
                new_conf['unitConfig'][key] = val

    # convert some values to list of strings
    for key in Keys.list_of_strings:
        if key not in new_conf:
            continue
        new_conf[key] = new_conf[key].strip().split(' ')
    return new_conf


def sort_dict(nix_dict: dict) -> dict:
    new_dict = {}
    for key in list(sorted(Keys.all)) + ["environment", "unitConfig", "serviceConfig"]:
        if key in nix_dict:
            new_dict[key] = nix_dict[key]
    return new_dict


def dict2nix(d: dict) -> str:
    s = json.dumps(d, indent=2)
    splitter = '  "environment": {'
    head, rest = s.split(splitter)
    rest = splitter + rest

    head = head.\
        replace('":', ' =').\
        replace('],', '];'). \
        replace('",\n  ]', '"\n  ]'). \
        replace('",\n    "', '"\n    "'). \
        replace('",\n', '";\n'). \
        replace('\n  "', '\n  ')

    rest = rest.\
        replace('  "', '  ').\
        replace('":', ' =').\
        replace('",\n', '";\n').\
        replace('"\n', '";\n').\
        replace('  },', '  };').\
        replace('  }\n', '  };\n')

    return head + rest


def parse_unit_file(file_content: str) -> dict:
    config = {}
    section = None
    for line in file_content.splitlines():
        match = re.fullmatch(r"^\[(\w*)\]$", line)
        if match:
            section = match.groups()[0]
            if section not in config:
                config[section] = {}
            continue
        match = re.fullmatch(r"^(\w*)=(.*)$", line)
        if not match:
            continue
        if not section:
            print("ERROR: Entry without section", file=sys.stderr)
            exit(1)
        key, val = match.groups()
        # option assignment with empty value resets option
        if key not in config[section] or val == '':
            config[section][key] = []
        config[section][key].append(val)
    for section in config.values():
        for key, val in section.items():
            section[key] = ' '.join(val)
    return config


def parse_args():
    parser = ArgumentParser(
        description="Convert systemd service files to nixpkgs syntax",
        usage='systemd2nix < example.service')
    return parser.parse_args()


def main():
    parse_args()  # just to display usage
    _input = sys.stdin.read()
    config = parse_unit_file(_input)
    formatted = format_config(config)
    print(dict2nix(sort_dict(formatted)))


if __name__ == '__main__':
    main()
