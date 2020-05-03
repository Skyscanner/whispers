from pathlib import Path

from lxml import etree as ElementTree

from whispers.log import debug
from whispers.plugins.uri import Uri
from whispers.rules import WhisperRules


class Xml:
    def __init__(self):
        self.breadcrumbs = []
        self.rules = WhisperRules()

    def pairs(self, filepath: Path):
        def _traverse(tree):
            """Traverse XML document"""
            for event, element in tree:
                if event == "start":
                    self.breadcrumbs.append(element.tag)
                elif event == "end":
                    self.breadcrumbs.pop()
                    continue

                # Format: <elem key="value">
                for key, value in element.attrib.items():
                    yield key, value, self.breadcrumbs

                    # Format: <elem name="jdbc:mysql://host?k1=v1&amp;k2=v2">
                    if self.rules.match("uri", value):
                        for k, v in Uri().pairs(value):
                            yield k, v, self.breadcrumbs

                # Format: <key>value</key>
                if not element.text:
                    continue
                yield element.tag, element.text, self.breadcrumbs

                # Format: <elem>key=value</elem>
                if "=" in element.text:
                    item = element.text.split("=")
                    if len(item) == 2:
                        yield item[0], item[1], self.breadcrumbs

                # Format: <key>name</key><value>string</value>
                found_key = None
                found_value = None
                for item in element:
                    if str(item.tag).lower() == "key":
                        found_key = item.text
                    elif str(item.tag).lower() == "value":
                        found_value = item.text
                if found_key and found_value:
                    yield found_key, found_value, self.breadcrumbs

        try:
            parser = ElementTree.XMLParser(recover=True)
            tree = ElementTree.parse(filepath.as_posix(), parser)
            tree = ElementTree.iterwalk(tree, events=("start", "end"))
            yield from _traverse(tree)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")
