import csv
import functools
import logging
import re

from utils import parse_item

__all__ = ['LogsParser']


def parse_user(username):
    return frozenset(username.split())


class LogsParser:
    VIEW_ACTIVITY_REGEX = re.compile(
        r"The user with id '(?P<user_id>\w+)' viewed the"
        r" '(?P<activity>\w+)' activity with course module"
        r" id '(?P<module_id>\w+)'")
    CONTENT_REGEX = re.compile(
        r"The user with id '(?P<user_id>\w+)' has viewed the content page "
        r"with id '16320' in the lesson activity "
        r"with course module id '(?P<module_id>\w+)'."
    )

    def __init__(self, log, delimiter):
        self._processors = [self._process_view, self._process_course]
        self.users = {}
        self.modules = {}
        self.activity = []
        self.workshops = {}
        self.course = ''
        self._parse(log, delimiter)

    def _process_view(self, item):
        activity_match = self.VIEW_ACTIVITY_REGEX.match(item['Описание'])
        content_match = self.CONTENT_REGEX.match(item['Описание'])
        if activity_match:
            if not activity_match['activity'] in (
                    'forum', 'page', 'quiz', 'resource', 'workshop', 'lesson'):
                return

            content_piece_type = activity_match['activity']
            user_id = activity_match['user_id']
            module_id = activity_match['module_id']
        elif content_match:
            content_piece_type = 'content_page'
            user_id = content_match['user_id']
            module_id = content_match['module_id']
        else:
            return

        self.users[user_id] = parse_user(
            item['Полное имя пользователя'])
        self.modules[module_id] = item['Контекст события']

        self.activity.append(
            (user_id, module_id, content_piece_type))

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
                raise e

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
