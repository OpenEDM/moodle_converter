#!/usr/bin/env python3

import argparse
import os.path
import sys

import converter


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--log-encoding', type=str, default='cp1251',
        help='Log file encoding')
    parser.add_argument(
        '-E', '--quests-encoding', type=str, default='utf-8-sig',
        help='Quests file encoding')
    parser.add_argument(
        '-l', '--logs', type=str, required=True, help='Log file')
    parser.add_argument(
        '-s', '--struct', type=str, help='Course structure XML file')
    parser.add_argument(
        '-d', '--delimiter', type=str, default=';',
        help='Log columns delimiter')
    parser.add_argument(
        '-q', '--quests', nargs='+', type=str, help='Quest answers log')
    parser.add_argument('output', type=str, help='Output csv prefix')
    return parser.parse_args()


def main():
    params = parse_args()

    if os.path.isdir(params.output):
        params.output = os.path.join(params.output, 'csv')

    converter.convert(
        params.logs, params.struct, params.quests,
        params.quests_encoding, params.log_encoding, params.delimiter,
        params.output)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
