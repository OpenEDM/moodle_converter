import csv
import functools
import logging
import re

from utils import parse_time, parse_item


__all__ = ['LogsParser']


def parse_user(username):
    return frozenset(username.split())


class LogsParser:
    VIEW_ACTIVITY_REGEX = re.compile(
        r"The user with id '(?P<user_id>\w+)' viewed the"
        r" '(?P<activity>\w+)' activity with course module"
        r" id '(?P<module_id>\w+)'")

    def __init__(self, log, delimiter):
        self._processors = [self._process_view, self._process_course]
        self.users = {}
        self.modules = {}
        self.activity = []
        self.workshops = {}
        self.course = ''
        self._parse(log, delimiter)

    def _process_view(self, item):
        match = self.VIEW_ACTIVITY_REGEX.match(item['Описание'])
        if not match:
            return

        if not match['activity'] in ('forum', 'page', 'quiz', 'resource', 'workshop'):
            return

        self.users[match['user_id']] = parse_user(
            item['Полное имя пользователя'])
        self.modules[match['module_id']] = item['Контекст события']


        self.activity.append(
            (match['user_id'], match['module_id'], match['activity']))

    def _process_course(self, item):
        context = item['Контекст события']
        if context.startswith('Курс: '):
            self.course = context[5:].strip(', ')

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
        for (test_id, test_name) in self.modules.items():
            if test_name.startswith('Тест: '):
                yield (parse_item(test_name), test_id)

    def get_content(self):
        for (content_id, content_name) in self.modules.items():
            if not content_name.startswith('Тест: '):
                yield (parse_item(content_name), content_id)
