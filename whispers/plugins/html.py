from pathlib import Path

from bs4 import BeautifulSoup, Comment

from whispers.utils import truncate_all_space


class Html:
    def pairs(self, filepath: Path):
        soup = BeautifulSoup(filepath.read_text(), "lxml")
        comments = soup.find_all(text=lambda t: isinstance(t, Comment))
        for comment in comments:
            comment = truncate_all_space(comment)
            if len(comment):
                yield "comment", comment
