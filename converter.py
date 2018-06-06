import os.path

import csv5
import logs
import quests
import struct
from results import Parser


def convert(logs_file, struct_file, quests_file,
            quests_encoding, log_encoding, delimiter, output):
    questsp = {}
    for quest in (quests_file or []):
        with open(quest, encoding=quests_encoding) as f:
            filename = os.path.splitext(os.path.basename(quest))[0]
            questsp[filename] = quests.QuestsParser(f)

    with open(logs_file, encoding=log_encoding) as f:
        logp = logs.LogsParser(f, delimiter)

    with open(struct_file, encoding='utf-8-sig') as f:
        course = struct.StructParser(f)

    csv5.process_all_csvs(
        output, 'utf-8', Parser(logp, questsp, course))
