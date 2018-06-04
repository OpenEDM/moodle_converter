import collections
import re
import xml.etree.ElementTree as ET


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
                self.items[item.text] = (module_id, module_name)
