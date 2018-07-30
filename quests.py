import csv

from utils import group_n, parse_time

__all__ = ['QuestsParser']


def parse_name(name, surname):
    return frozenset(name.split()) | frozenset(surname.split())


class QuestsParser:
    def __init__(self, quests):
        self.answers = []
        self.quests = []
        self.quest_headers = []
        self._parse(quests)

    def _parse(self, quests):
        reader = csv.reader(quests, delimiter=',')
        headers = next(reader)
        if headers:
            self.quest_headers = headers[10::3]

        for (name, surname, _, _, _, _, time, _, _, _, *answers) in reader:
            quests = []
            item = [parse_name(name, surname), parse_time(time)]
            for (quest, answer, correct) in group_n(answers, 3):
                quests.append(quest)
                item.append(answer.strip() == correct.strip())

            self.quests = self.quests or quests
            self.answers.append(item)
