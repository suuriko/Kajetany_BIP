import abc
import logging
from typing import Generator, Optional

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

    def _get_node_text_content_or_default(
        self, node: Optional[LexborNode], default: Optional[str] = None
    ) -> Optional[str]:
        """Helper to get text content from a node or return default."""
        return node.text_content.strip() if node and node.text_content else default
