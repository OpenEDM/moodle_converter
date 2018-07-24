import collections
import logging

from utils import string_distance, parse_item


__all__ = ['Parser']


class FuzzyDict(dict):
    def __contains__(self, key):
        if super().__contains__(key):
            return True

        dist = min((string_distance(key, k), k) for k in self)
        return dist[0] < len(dist[1])/2

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            dist = min((string_distance(key, k), k) for k in self)
            if dist[0] < len(dist[1])/2:
                return super().__getitem__(dist[1])
            raise


def add_id(x):
    return 'ID_' + str(x)


class Parser:
    def __init__(self, logs, quests, struct, workshops):
        self._logs = logs
        self._quests = quests
        self._struct = struct
        self._prepare()
        self.item_id_by_text = dict()
        self.workshops = workshops

    def _prepare(self):
        self.test_ids = FuzzyDict(self._logs.get_tests())
        self.m_ids = {}

        self._modules = {}
        for (_, moduleid, activity) in self._logs.activity:
            if activity != 'quiz' and (moduleid in self._logs.modules):
                self._modules[moduleid] = (
                    activity, self._logs.modules[moduleid])

        # Dummy loop for generate IDs
        exist_items = set()
        for (moduleid, (_, name)) in self._modules.items():
            if name == 'Другие':
                continue
            info = self._struct.get_item(parse_item(name))
            if info:
                exist_items.add(info[0])

        for (_, (item, _, _, _)) in self._struct.get_items():
            if item in exist_items:
                self._get_id(item)

    def get_course_info(self):
        return {
            'short_name': self._logs.course,
            'long_name': self._logs.course
        }

    def get_student_solutions(self):
        for (qname, info) in self._quests.items():
            if qname not in self.test_ids:
                continue

            for (user, time, *results) in info.answers:
                userid = self._logs.get_user_id(user)
                if not userid:
                    continue

                for (index, value) in enumerate(results):
                    qid = self._struct.get_item(qname)[3]
                    yield (userid, add_id(qid), int(value), time)

    def get_student_content(self):
        viewed = collections.defaultdict(set)
        users = set()
        modules = set()

        for (userid, moduleid, activity) in self._logs.activity:
            users.add(userid)
            if activity != 'quiz':
                viewed[userid].add(moduleid)
                modules.add(moduleid)

        for user in users:
            for module in modules:
                yield (user, module, int(module in viewed[user]))

    @staticmethod
    def clean_name(name: str) -> str:
        return name.lstrip().rstrip().lower()

    def get_item_id_by_name(self, name):
        for key, value in self._logs.modules.items():
            if value.endswith(name):
                return key
        return None

    def get_assessments(self):
        for workshop in self.workshops:
            name = workshop.item_name
            item_id = self.get_item_id_by_name(name)
            if not item_id:
                logging.warning('Not found item with name "{}"'.format(name))
                continue
            for cross_attempt in workshop.cross_attempts:
                yield (cross_attempt['user_id'], add_id(item_id),
                       cross_attempt['reviewer_id'], cross_attempt['score'],
                       cross_attempt['max_score'])

    def _get_id(self, value):
        if value not in self.m_ids:
            self.m_ids[value] = len(self.m_ids) + 1
        return self.m_ids[value]

    def get_tasks(self):
        item_ids = set()
        for (qname, info) in self._quests.items():
            (mid, mname, item_type, item_id) = self._struct.get_item(qname)
            if item_id not in item_ids:
                item_ids.add(item_id)
                yield (add_id(item_id), item_type, qname, mid, self._get_id(mid), mname)

        for workshop in self.workshops:
            item_name = workshop.item_name
            if not item_name:
                continue
            (mid, mname, item_type, item_id) = self._struct.get_item(item_name)
            yield (add_id(item_id), item_type, item_name, mid, self._get_id(mid), mname)


    def get_content(self):
        for (moduleid, (module_type, name)) in self._modules.items():
            info = self._struct.get_item(parse_item(name))
            if info:
                yield (moduleid, module_type, name,
                       info[0], self._get_id(info[0]), info[1])
                continue
            if name != 'Другие':
                logging.warning(
                    'Item "%s" not found in course structure.', name)
                yield (moduleid, module_type, name, moduleid,
                       self._get_id(moduleid), 'NA')
