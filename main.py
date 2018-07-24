#!/usr/bin/env python3

import argparse
import logging
import os.path
import sys

import converter


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--log-encoding', type=str, default='utf-8-sig',
        help='Log file encoding')
    parser.add_argument(
        '-E', '--quests-encoding', type=str, default='utf-8-sig',
        help='Quests file encoding')
    parser.add_argument(
        '--workshops-encoding', type=str, default='utf-8-sig',
        help='Workshop files encoding')
    parser.add_argument(
        '-w', '--workshops', nargs='+', type=str,
        help='workshop.xml files'
    )
    parser.add_argument(
        '-l', '--logs', type=str, required=True, help='Log file')
    parser.add_argument(
        '-s', '--struct', type=str, help='Course structure XML file')
    parser.add_argument(
        '-d', '--delimiter', type=str, default=',',
        help='Log columns delimiter')
    parser.add_argument(
        '-q', '--quests', nargs='+', type=str, help='Quest answers log')
    parser.add_argument('output', type=str, help='Output csv prefix')
    return parser.parse_args()


def main():
    params = parse_args()

    if os.path.isdir(params.output):
        params.output = os.path.join(params.output, 'csv')

    logging.getLogger().setLevel(logging.INFO)
    converter.convert(
        params.logs, params.struct, params.quests, params.workshops,
        params.workshops_encoding, params.quests_encoding, params.log_encoding,
        params.delimiter, params.output)


if __name__ == '__main__':
    sys.exit(main())
