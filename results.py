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


class Parser:
    def __init__(self, logs, quests, struct):
        self._logs = logs
        self._quests = quests
        self._struct = struct
        self._prepare()

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

        for (_, (item, _)) in self._struct.get_items():
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
                    yield (userid, "ID_{:0>10}_{:0>10}".format(
                        self.test_ids[qname], index), int(value), time)

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

    def get_assessments(self):
        if False:
            yield

    def _get_id(self, value):
        if value not in self.m_ids:
            self.m_ids[value] = len(self.m_ids) + 1
        return self.m_ids[value]

    def get_tasks(self):
        for (qname, info) in self._quests.items():
            if qname not in self.test_ids:
                continue

            for (idx, text) in enumerate(info.quests):
                qid = self.test_ids[qname]
                test_name = self._logs.modules[qid][6:]
                (mid, mname) = self._struct.get_item(
                    test_name, (qid, test_name))
                yield ("ID_{:0>10}_{:0>10}".format(qid, idx),
                       'assign', text, mid, self._get_id(mid), mname)

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
