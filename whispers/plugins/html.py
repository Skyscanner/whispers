from pathlib import Path

from bs4 import BeautifulSoup, Comment
from bs4.element import PageElement

from whispers.utils import truncate_all_space


class Html:
    def pairs(self, filepath: Path):
        soup = BeautifulSoup(filepath.read_text(), "lxml")
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            yield from self.parse_comments(comment)

    def parse_comments(self, comment: PageElement):
        comment = truncate_all_space(comment.extract()).strip()
        if comment:
            yield "comment", comment
