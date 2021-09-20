from pathlib import Path
from typing import Iterator

from bs4 import BeautifulSoup, Comment

from whispers.core.utils import KeyValuePair, truncate_all_space


class Html:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        soup = BeautifulSoup(filepath.read_text(), "lxml")
        key = "comment"
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment = truncate_all_space(comment.extract()).strip()
            if comment:
                yield KeyValuePair(key, comment, [key])
