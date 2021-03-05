from pathlib import Path

from bs4 import BeautifulSoup, Comment

from whispers.utils import strip_string


class Html:
    def pairs(self, filepath: Path):
        soup = BeautifulSoup(filepath.read_text(), "lxml")
        comments = soup.find_all(text=lambda t: isinstance(t, Comment))
        for comment in comments:
            comment = strip_string(comment)
            if len(comment):
                yield "comment", comment
