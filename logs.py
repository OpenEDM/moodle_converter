import csv
import functools
import logging
import re

from utils import parse_time


__all__ = ['LogsParser']


def parse_user(username):
    return frozenset(username.split())


class LogsParser:
    VIEW_ACTIVITY_REGEX = re.compile(
        r"The user with id '(\w+)' viewed the '(\w+)' activity"
        r" with course module id '(\w+)'")

    def __init__(self, log, delimiter):
        self._processors = [self._process_view]
        self.users = {}
        self.modules = {}
        self.activity = []
        self._parse(log, delimiter)

    def _process_view(self, item):
        match = self.VIEW_ACTIVITY_REGEX.match(item['Описание'])
        if not match:
            return

        self.users[match[1]] = parse_user(item['Полное имя пользователя'])
        self.modules[match[3]] = item['Контекст события']
        self.activity.append((match[1], match[3], match[2]))

    def _parse(self, log, delimiter):
        reader = csv.DictReader(log, delimiter=delimiter)
        for (i, item) in enumerate(reader):
            try:
                for processor in self._processors:
                    processor(item)
            except Exception as e:
                logging.warning(
                    'Error on process entry, line %d: %s. Skip', i + 2, e)

    @functools.lru_cache()
    def get_user_id(self, user):
        if not isinstance(user, (set, frozenset)):
            user = parse_user(user)

        for (userid, username) in self.users.items():
            if len(username & user) >= 2:
                return userid

    def get_tests(self):
        for (testid, testname) in self.modules.items():
            if testname.startswith('Тест: '):
                yield (testname[6:].strip(), testid)
