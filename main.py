#!/usr/bin/env python3

import argparse
import os.path
import sys

import csv5
import quests
import logs
from results import Parser


def parse_args():
    aparser = argparse.ArgumentParser()
    aparser.add_argument(
        '-e', '--log-encoding', type=str, default='cp1251',
        help='Log file encoding')
    aparser.add_argument(
        '-E', '--quests-encoding', type=str, default='utf-8-sig',
        help='Quests file encoding')
    aparser.add_argument(
        '-l', '--logs', type=str, required=True, help='Log file')
    aparser.add_argument(
        '-q', '--quests', nargs='+', type=str, help='Quest answers log')
    aparser.add_argument('output', type=str, help='Output csv prefix')
    return aparser.parse_args()


def main():
    params = parse_args()

    questsp = {}
    for quest in (params.quests or []):
        with open(quest, encoding=params.quests_encoding) as f:
            filename = os.path.splitext(os.path.basename(quest))[0]
            questsp[filename] = quests.QuestsParser(f)

    with open(params.logs, encoding=params.log_encoding) as f:
        logp = logs.LogsParser(f)

    if os.path.isdir(params.output):
        params.output = os.path.join(params.output, 'csv')

    csv5.process_all_csvs(params.output, 'utf-8', Parser(logp, questsp))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
