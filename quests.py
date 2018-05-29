import csv
import re


__all__ = ['QuestsParser']


MONTH = dict([(s, i + 1) for (i, s) in enumerate([
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
])])

TIME_REGEX = re.compile(r'(\d+)\s+(\w+)\s+(\d+)\s+(\d+):(\d+)')


def parse_name(name, surname):
    return frozenset(name.split()) | frozenset(surname.split())


def parse_time(time):
    parsed = TIME_REGEX.match(time)
    return '{:>02}.{:>02}.{} {:>02}:{:>02}:00'.format(
        parsed[1], MONTH[parsed[2]], parsed[3], parsed[4], parsed[5])


def group_n(iterable, n):
    return zip(*([iter(iterable)]*n))


class QuestsParser:
    def __init__(self, quests):
        self.answers = []
        self.quests = []
        self._parse(quests)

    def _parse(self, quests):
        reader = csv.reader(quests, delimiter=',')
        next(reader)

        for (name, surname, _, _, _, _, time, _, _, _, *answers) in reader:
            quests = []
            item = [parse_name(name, surname), parse_time(time)]
            for (quest, answer, correct) in group_n(answers, 3):
                quests.append(quest)
                item.append(answer.strip() == correct.strip())

            self.quests = self.quests or quests
            self.answers.append(item)
