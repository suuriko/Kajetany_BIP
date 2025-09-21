import abc
import io
import logging
from typing import Generator, Optional

from pypdf import PdfReader
from selectolax.lexbor import LexborNode

from src.crawler.http_client import HttpClient, HttpResponse
from src.models.elements import ContentItem


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

    def fetch(self, url: str) -> HttpResponse:
        """Fetch the content of the given URL. Optionally transform it before returning.

        Args:
            url: URL to fetch

        Returns:
            HTTP response object
        """
        return self.http_client.fetch(url)

    @abc.abstractmethod
    def parse_list(self, html: str) -> Generator[Optional[ContentItem], None, None]:
        """Parse HTML content and yield Elements objects.

        Args:
            html: HTML content to parse

        Yields:
            Elements objects found in the content, or None if no matches
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_item(self, item: LexborNode) -> Optional[ContentItem]:
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
