from pathlib import Path
from typing import Iterator

from lxml import etree as ElementTree

from whispers.core.log import global_exception_handler
from whispers.core.utils import KeyValuePair, is_uri
from whispers.plugins.uri import Uri


class Xml:
    def __init__(self):
        self.keypath = []

    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        def _traverse(tree):
            """Traverse XML document"""
            for event, element in tree:
                if event == "end":
                    self.keypath.pop()
                    continue

                self.keypath.append(element.tag)

                # Format: <elem key="value">
                for key, value in element.attrib.items():
                    self.keypath.append(key)
                    yield KeyValuePair(key, value, list(self.keypath))

                    # Format: <elem name="jdbc:mysql://host?k1=v1&amp;k2=v2">
                    if is_uri(value):
                        for pair in Uri().pairs(value):
                            pair.keypath = self.keypath + [pair.key]
                            yield pair

                    self.keypath.pop()

                # Format: <key>value</key>
                if not element.text:
                    continue

                yield KeyValuePair(element.tag, element.text, list(self.keypath))

                # Format: <elem>key=value</elem>
                if "=" in element.text:
                    item = element.text.split("=")
                    if len(item) == 2:
                        self.keypath.append(item[0])
                        yield KeyValuePair(item[0], item[1], list(self.keypath))
                        self.keypath.pop()

                # Format: <key>name</key><value>string</value>
                found_key = None
                found_value = None
                for item in element:
                    if str(item.tag).lower() == "key":
                        found_key = item.text
                    elif str(item.tag).lower() == "value":
                        found_value = item.text

                if found_key and found_value:
                    self.keypath.append(found_key)
                    yield KeyValuePair(found_key, found_value, list(self.keypath))
                    self.keypath.pop()

        try:
            parser = ElementTree.XMLParser(recover=True)
            tree = ElementTree.parse(filepath.as_posix(), parser)
            tree = ElementTree.iterwalk(tree, events=("start", "end"))
            yield from _traverse(tree)
        except Exception:
            global_exception_handler(filepath.as_posix(), tree)
