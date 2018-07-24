import contextlib
import re

__all__ = ['parse_time', 'group_n', 'parse_item', 'starts_with', 'nfind']


TIME_REGEX1 = re.compile(r'(\d+)/(\d+)/(\d+),\s+(\d+):(\d+)')
TIME_REGEX2 = re.compile(r'(\d+)\s+(\w+)\s+(\d+)\s+(\d+):(\d+)')
TIME_FORMAT = '{:>02}.{:>02}.{} {:>02}:{:>02}:{:>02}'

MONTH = dict([(s, i + 1) for (i, s) in enumerate([
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
])])


def parse_time(time):
    for regex in (TIME_REGEX1, TIME_REGEX2):
        with contextlib.suppress(Exception):
            parsed = regex.match(time)
            return TIME_FORMAT.format(
                parsed[1], MONTH.get(parsed[2], parsed[2]),
                parsed[3], parsed[4], parsed[5], 0)


def group_n(iterable, n):
    return zip(*([iter(iterable)]*n))


def string_distance(string1, string2):
    string1 = ''.join(re.findall(r'\w', string1)).casefold()
    string2 = ''.join(re.findall(r'\w', string2)).casefold()

    dist = list(range(len(string1) + 1))
    for i in range(1, len(string2) + 1):
        (prev_dist, dist) = (dist, [i] + [0]*len(string1))
        for j in range(1, len(string1) + 1):
            dist[j] = min(
                prev_dist[j] + 1, dist[j - 1] + 1,
                prev_dist[j - 1] + int(string1[j - 1] != string2[i - 1]))

    return dist[-1]


def parse_item(name):
    return name.split(':', 1)[-1][1:]


def starts_with(string, prefixes):
    return any(string.startswith(prefix) for prefix in prefixes)


def nfind(string, sub, n=1):
    start = -1
    for _ in range(n):
        start = string.find(sub, start + 1)
        if start < 0:
            return -1
    return start
