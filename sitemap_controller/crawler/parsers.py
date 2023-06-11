from abc import ABC, abstractclassmethod
from typing import List
from lxml import cssselect, html
import re


class BaseParser(ABC):
    @abstractclassmethod
    def parse(cls, html_string) -> List[str]:
        """
        Base parse method
        """


class Parser(BaseParser):
    """
    LXML based Parser
    """

    @classmethod
    def parse(cls, html_string):
        dochtml = html.fromstring(html_string)
        select = cssselect.CSSSelector("a")
        return [el.get("href") for el in select(dochtml)]


class ReParser(BaseParser):
    @classmethod
    def parse(cls, html_string):
        return re.findall(r"(?i)href\s*?=\s*?[\"\']?([^\s\"\'<>]+)[\"\']", html_string)
