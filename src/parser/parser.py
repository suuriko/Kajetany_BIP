import abc
import io
import logging
import re
from datetime import datetime
from urllib.parse import urljoin

from pypdf import PdfReader
from selectolax.parser import HTMLParser, Node

from src.crawler.http_client import HttpClient
from src.models.elements import Elements

KAJETANY_RE = re.compile(r"\bKajetan\w*\b", re.IGNORECASE)
LIST_URLS = [
    "https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia",
    # "https://bip.nadarzyn.pl/975,procedury-planistyczne-w-toku"
    # dodaj inne, jeśli chcesz
]

logger = logging.getLogger("parser")
i = 0


class BaseParser(abc.ABC):
    def __init__(self):
        self.logger = logging.getLogger("parser")
        self.i = 0

    def parse_list(
        self,
        html: str,
        base_url: str,
        http_client: HttpClient,
    ):
        raise NotImplementedError


class BipNadarzynParser(BaseParser):
    def parse_list(
        self,
        html: str,
        base_url: str,
        http_client: HttpClient,
    ):
        dom = HTMLParser(html)
        for item in dom.css("#PageContent div.obiekt"):
            if "Kajetan" in item.text():
                yield self.get_parsing_details(item, base_url)
            else:
                for a in item.css("a"):  # zawęź selektor po rozpoznaniu drzewa
                    href = a.attributes.get("href", "")
                    if href is None or not href.lower().endswith(".pdf"):
                        continue
                    pdf_url = urljoin(base_url, href)
                    pr = http_client.fetch(pdf_url)
                    if self.pdf_text_has_kajetany(pr.content):
                        yield self.get_parsing_details(item, base_url)

    def get_parsing_details(self, item: Node, base_url: str) -> Elements | None:
        h3_node = item.css_first("h3")
        if h3_node is None:
            return None

        title = h3_node.text()
        for a in item.css("a"):  # zawęź selektor po rozpoznaniu drzewa
            href = a.attributes.get("href", "")
            text = (a.text() or "").strip()
            if not href or not text:
                continue
            full_url = urljoin(base_url, href)  # <— zamiast httpx.URL(..., base=...)
            logger.info(f"Found link in list: \n{title} \n -> {text} \n  -> {full_url}")

            return Elements(main_title=title, title=text, url=full_url, published_at=self.extract_date(title))

    def extract_date(self, text: str):
        match = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d.%m.%Y").date()
            except ValueError:
                return None
        return None

    def pdf_text_has_kajetany(self, content_bytes: bytes) -> bool:
        global i
        i += 1
        print(f"PDF check {i}")

        reader = PdfReader(io.BytesIO(content_bytes))
        txt = "".join([p.extract_text() or "" for p in reader.pages])
        return bool(KAJETANY_RE.search(txt))
