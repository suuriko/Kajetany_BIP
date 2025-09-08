import abc
import io
import logging
import re
from typing import Generator, Optional
from urllib.parse import urljoin

from pypdf import PdfReader
from selectolax.parser import HTMLParser, Node

from src.crawler.datetime_extractor import extract_datetime
from src.crawler.http_client import HttpClient
from src.models.elements import Elements


class BaseParser(abc.ABC):
    """Abstract base class for parsing content from BIP websites.

    This class provides common functionality for parsing HTML content and PDF files,
    while allowing specific implementations to define their own parsing logic.
    """

    def __init__(self, http_client: HttpClient, base_url: str) -> None:
        """Initialize the parser with HTTP client and base URL.

        Args:
            http_client: HTTP client for making requests
            base_url: Base URL for resolving relative links
        """
        self.logger = logging.getLogger("parser")
        self.http_client = http_client
        self.base_url = base_url
        self.i = 0

    @abc.abstractmethod
    def parse_list(self, html: str) -> Generator[Optional[Elements], None, None]:
        """Parse HTML content and yield Elements objects.

        Args:
            html: HTML content to parse

        Yields:
            Elements objects found in the content, or None if no matches
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_item(self, item: Node) -> Optional[Elements]:
        """Parse a single HTML item node into an Elements object.

        Args:
            item: HTML node to parse

        Returns:
            Elements object or None if parsing fails
        """
        raise NotImplementedError

    def parse_pdf(self, url: str) -> str:
        """Extract text content from a PDF at the given URL.

        Args:
            url: URL of the PDF to parse

        Returns:
            Extracted text content from all pages
        """
        response = self.http_client.fetch(url)
        reader = PdfReader(io.BytesIO(response.content))
        return "".join([p.extract_text() or "" for p in reader.pages])


class BipNadarzynParser(BaseParser):
    """Parser for BIP Nadarzyn website content.

    Searches for content related to Kajetany in both HTML text and PDF documents.
    """

    SEARCH_PATTERN = re.compile(r"\bKajetan\w*\b", re.IGNORECASE)

    def parse_list(self, html: str) -> Generator[Optional[Elements], None, None]:
        """Parse the main list page for relevant items."""
        dom = HTMLParser(html)
        for item in dom.css("#PageContent div.obiekt"):
            # First, match directly in HTML text
            if self._text_matches_pattern(item.text()):
                yield self.parse_item(item)
                continue

            # Otherwise, fall back to checking linked PDFs
            if self._pdf_links_have_match(item):
                yield self.parse_item(item)

    def _pdf_links_have_match(self, item: Node) -> bool:
        """Return True if any PDF linked within the item contains the search pattern."""
        for a in item.css("a"):
            href = a.attributes.get("href")
            if href is None or not href.lower().endswith(".pdf"):
                continue
            pdf_url = urljoin(self.base_url, href)
            self.i += 1
            self.logger.debug(f"PDF check {self.i}")
            if self._pdf_text_has_match(pdf_url):
                return True
        return False

    def parse_item(self, item: Node) -> Optional[Elements]:
        """Parse a single item node into an Elements object."""
        title = self._get_node_text_or_default(item.css_first("h3")) or "Brak tytułu"
        published_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".data_publikacji .system_metryka_wartosc"))
        )
        created_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".autor_data .system_metryka_wartosc"))
        )
        last_modified_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".data_mod .system_metryka_wartosc"))
        )

        for a in item.css("a"):
            href = a.attributes.get("href", "")
            link_text = (a.text() or "").strip()
            if not href or not link_text:
                continue
            full_url = urljoin(self.base_url, href)
            self.logger.info(f"Found link in list: \n{title} \n -> {link_text} \n  -> {full_url}")

            return Elements(
                main_title=title,
                title=link_text,
                url=full_url,
                published_at=published_at,
                created_at=created_at,
                last_modified_at=last_modified_at,
            )
        return None

    def _get_node_text_or_default(self, node: Optional[Node], default: Optional[str] = None) -> Optional[str]:
        """Helper to get text from a node or return default."""
        return node.text().strip() if node else default

    def _text_matches_pattern(self, text: str) -> bool:
        """Check if text matches the search pattern."""
        return bool(self.SEARCH_PATTERN.search(text))

    def _pdf_text_has_match(self, url: str) -> bool:
        """Check if PDF content contains the search pattern."""
        try:
            pdf_text_content = self.parse_pdf(url)
            return self._text_matches_pattern(pdf_text_content)
        except Exception as e:
            self.logger.warning(f"Failed to parse PDF {url}: {e}")
            return False
