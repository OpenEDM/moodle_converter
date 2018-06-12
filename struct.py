import collections
import functools
import logging
import re
import xml.etree.ElementTree as ET

from utils import starts_with, nfind


XMLNS_RE = re.compile(r' xmlns="[^"]+"')


class StructParser:
    def __init__(self, struct):
        self.items = collections.OrderedDict()
        self._parse(struct)

    def _parse(self, struct):
        text = struct.read().replace('&nbsp;', '&#160;')
        tree = ET.fromstring(XMLNS_RE.sub('', text, count=1))

        for child in tree.find(".//item[@identifier='root']"):
            module_id = child.attrib['identifier']
            module_name = child.find("./title").text.strip()
            for item in child.findall(".//item/title"):
                if not item.text:
                    continue

                if (item.text in self.items and
                        self.items[item.text][0] != module_id):
                    logging.warning(
                        'Duplicate items: "%s". Second item (with'
                        ' module_id="%s" and module_name="%s") will be skip',
                        item.text, module_id, module_name)
                    continue

                self.items[item.text] = (module_id, module_name)

    def get_items(self):
        return self.items.items()

    def get_item(self, text, default=None):
        if text in self.items:
            return self.items[text]

        if default:
            return self._guess_item(text) or default

        return default

    @functools.lru_cache()
    def _guess_item(self, text):
        text_ = text.casefold()

        if starts_with(text_, ['вопросы для самопроверки к ',
                               'вопросы для самопроверки по ']):
            item = text_[nfind(text_, ' ', 4):].strip()
            for (name, (module_id, module_name)) in self.get_items():
                if not starts_with(name.casefold(), [item + ' ', item + '.']):
                    continue

                logging.info('Guessed "%s": module "%s"', text, module_name)
                return (module_id, module_name)

        if starts_with(text_, ['контрольный тест к ',
                               'контрольный тест по ']):
            item = (text_[nfind(text_, ' ', 3):].strip()
                    .replace('разделу', 'раздел'))
            for (_, (module_id, module_name)) in self.get_items():
                if not starts_with(module_name.casefold(),
                                   [item + ' ', item + '.']):
                    continue

                logging.info('Guessed "%s": module "%s"', text, module_name)
                return (module_id, module_name)

        return None
