import abc
import logging
from datetime import datetime
from typing import Generator, Optional
from urllib.parse import urlparse

from selectolax.lexbor import LexborHTMLParser, LexborNode

from src.models.elements import ContentItem, RedirectItem


class BaseParser(abc.ABC):
    """Abstract base class for parsing content from websites.

    This class provides common functionality for parsing HTML content,
    while allowing specific implementations to define their own parsing logic.
    """

    def __init__(self) -> None:
        """Initialize the parser with base URL.

        Args:
            base_url: Base URL for resolving relative links
        """
        self.logger = logging.getLogger("parser")

    @abc.abstractmethod
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        """Determine if this parser can handle the given URL and DOM.

        Args:
            url: The URL to check
            dom: The parsed HTML DOM
        Returns:
            True if this parser can handle the URL, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem | RedirectItem]]:
        """Parse the given DOM and return an Elements or Redirect object.

        Args:
            dom: The parsed HTML DOM
        Returns:
            An Elements object if parsing is successful, None otherwise
        """
        raise NotImplementedError

    def _get_node_text_or_default(self, node: Optional[LexborNode], default: Optional[str] = None) -> Optional[str]:
        """Helper to get text from a node or return default."""
        return node.text(strip=True) if node else default

    def _safe_get_node(self, parent_node: Optional[LexborNode], selector: str) -> Optional[LexborNode]:
        """Safely get a child node using CSS selector."""
        return parent_node.css_first(selector) if parent_node else None

    def _extract_title(self, node: Optional[LexborNode], default: str = "Brak tytułu") -> str:
        """Extract title from h3 element."""
        title_node = self._safe_get_node(node, "h3")
        return self._get_node_text_or_default(title_node) or default

    def _get_anchor_from_url(self, url: str) -> str:
        """Extract anchor from URL fragment."""
        return urlparse(url).fragment

    def _extract_metadata(
        self, node: Optional[LexborNode]
    ) -> tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        """Extract publication, creation and modification dates from article node.

        Args:
            node: The article node to extract metadata from

        Returns:
            Tuple of (published_at, created_at, last_modified_at)
        """
        if not node:
            return None, None, None

        from src.crawler.datetime_extractor import extract_datetime

        published_at = extract_datetime(
            self._get_node_text_or_default(self._safe_get_node(node, ".data_publikacji .system_metryka_wartosc"))
        )
        created_at = extract_datetime(
            self._get_node_text_or_default(self._safe_get_node(node, ".autor_data .system_metryka_wartosc"))
        )
        last_modified_at = extract_datetime(
            self._get_node_text_or_default(self._safe_get_node(node, ".data_mod .system_metryka_wartosc"))
        )

        return published_at, created_at, last_modified_at

    def _get_node_text_content_or_default(
        self, node: Optional[LexborNode], default: Optional[str] = None
    ) -> Optional[str]:
        """Helper to get text content from a node or return default."""
        return node.text_content.strip() if node and node.text_content else default
