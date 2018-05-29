import collections


__all__ = ['Parser']


class Parser:
    def __init__(self, logs, quests):
        self._logs = logs
        self._quests = quests
        self._prepare()

    def _prepare(self):
        self.test_ids = dict(self._logs.get_tests())

    def get_student_solutions(self):
        for (qname, info) in self._quests.items():
            if qname not in self.test_ids:
                continue

            for (user, time, *results) in info.answers:
                userid = self._logs.get_user_id(user)
                if not userid:
                    continue

                for (index, value) in enumerate(results):
                    yield (userid, "{:0>10} {:0>10}".format(
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

    def get_tasks(self):
        for (qname, info) in self._quests.items():
            if qname not in self.test_ids:
                continue

            for (index, text) in enumerate(info.quests):
                yield ("{:0>10} {:0>10}".format(self.test_ids[qname], index),
                       'assign', text, 'NA', 'NA', 'NA')

    def get_content(self):
        modules = {}
        for (_, moduleid, activity) in self._logs.activity:
            if activity != 'quiz' and (moduleid in self._logs.modules):
                modules[moduleid] = (activity, self._logs.modules[moduleid])

        for (moduleid, (module_type, name)) in modules.items():
            yield (moduleid, module_type, name, 'NA', 'NA', 'NA')
