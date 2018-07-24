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
        self.modules = collections.OrderedDict()
        self._parse(struct)

    def _parse(self, struct):
        text = struct.read().replace('&nbsp;', '&#160;')
        tree = ET.fromstring(XMLNS_RE.sub('', text, count=1))

        for child in tree.find(".//sections"):
            module_id = child.find('./sectionid').text
            module_name = child.find('./title').text
            self.modules[module_id] = module_name

        for child in tree.find(".//activities"):
            module_id = child.find('./sectionid').text
            item_type = child.find('./modulename').text
            item_id = child.find('./moduleid').text
            item_name = child.find("./title").text
            module_name = self.modules.get(module_id, None)
            if not module_name:
                logging.warning(
                    'Not found Module name for item. Item id: "{}"; '
                    'Item name: "{}"; Module name: "{}"'.format(item_id,
                                                                item_name,
                                                                module_name))
                continue
            self.items[item_name] = (module_id, module_name, item_type, item_id)

    def get_items(self):
        return self.items.items()

    def get_item(self, text, default=None):
        if text in self.items:
            return self.items[text]

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
