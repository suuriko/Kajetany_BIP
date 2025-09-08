import abc
import io
import logging
import re
from datetime import datetime
from typing import Generator
from urllib.parse import urljoin

from pypdf import PdfReader
from selectolax.parser import HTMLParser, Node

from src.crawler.http_client import HttpClient
from src.models.elements import Elements


class BaseParser(abc.ABC):
    def __init__(self, http_client: HttpClient, base_url: str):
        self.logger = logging.getLogger("parser")
        self.http_client = http_client
        self.base_url = base_url
        self.i = 0

    @abc.abstractmethod
    def parse_list(
        self,
        html: str,
    ) -> Generator[Elements | None]:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_item(self, item: Node) -> Elements | None:
        raise NotImplementedError

    def parse_pdf(self, url: str) -> str:
        response = self.http_client.fetch(url)
        reader = PdfReader(io.BytesIO(response.content))
        return "".join([p.extract_text() or "" for p in reader.pages])


class BipNadarzynParser(BaseParser):
    def parse_list(
        self,
        html: str,
    ) -> Generator[Elements | None]:
        dom = HTMLParser(html)
        for item in dom.css("#PageContent div.obiekt"):
            if self._text_matches_pattern(item.text()):
                yield self.parse_item(item)
            else:
                for a in item.css("a"):
                    href = a.attributes.get("href")
                    if href is None or not href.lower().endswith(".pdf"):
                        continue
                    pdf_url = urljoin(self.base_url, href)
                    self.i += 1
                    self.logger.debug(f"PDF check {self.i}")
                    if self._pdf_text_has_match(pdf_url):
                        yield self.parse_item(item)

    def parse_item(self, item: Node) -> Elements | None:
        h3_node = item.css_first("h3")
        title = h3_node.text() if h3_node else "Brak tytułu"
        for a in item.css("a"):
            href = a.attributes.get("href", "")
            link_text = (a.text() or "").strip()
            if not href or not link_text:
                continue
            full_url = urljoin(self.base_url, href)
            self.logger.info(f"Found link in list: \n{title} \n -> {link_text} \n  -> {full_url}")

            return Elements(main_title=title, title=link_text, url=full_url, published_at=self._extract_date(title))

    def _text_matches_pattern(self, text: str) -> bool:
        pattern = re.compile(r"\bKajetan\w*\b", re.IGNORECASE)
        return bool(pattern.search(text))

    def _extract_date(self, text: str):
        match = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d.%m.%Y").date()
            except ValueError:
                return None
        return None

    def _pdf_text_has_match(self, url: str) -> bool:
        pdf_text_content = self.parse_pdf(url)
        return self._text_matches_pattern(pdf_text_content)
