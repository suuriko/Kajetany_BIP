import logging
import time
from typing import Generator

from selectolax.lexbor import LexborHTMLParser

from src.crawler.http_client import HttpClient
from src.crawler.nadarzyn_bip.base_parser import BaseParser
from src.models import ContentItem, RedirectItem


class Crawler:
    """Orchestrates web crawling using multiple parsers.

    Manages HTTP client lifecycle and coordinates parsing of multiple URLs
    with their respective parser implementations.
    """

    def __init__(self, base_url: str, parsers: list[BaseParser]) -> None:
        """Initialize crawler with URL-parser mappings.

        Args:
            base_url: The base URL for the crawler
            parsers: List of parser instances to use for crawling
        """
        self.logger = logging.getLogger("crawler")
        self.base_url = base_url
        self.parsers = parsers

    def crawl(self) -> list[ContentItem]:
        """Crawl all configured URLs and return new items.

        Args:
            past_items: List of previously found items

        Returns:
            DataFrame containing newly found items
        """
        new_items: list[ContentItem] = []
        items_to_crawl: list[RedirectItem] = [RedirectItem(url=self.base_url)]

        with HttpClient() as client:
            for item_to_crawl in items_to_crawl:
                for item in self.crawl_url(item_to_crawl.url, client):
                    if item is None:
                        self.logger.warning(f"Parser returned no item for {item_to_crawl.url}")
                        continue
                    if isinstance(item, RedirectItem):
                        self.logger.info(f"Found redirect to {item.url}, adding to crawl list")
                        items_to_crawl.append(item)
                        continue

                    merged_item = item.merge_with_redirect(item_to_crawl)

                    self.logger.info(f"Item parsed:\n{merged_item}")
                    new_items.append(merged_item)

                self.logger.info("")
                time.sleep(1.5)  # Be respectful to the server

        return new_items

    def crawl_url(self, url: str, client: HttpClient) -> Generator[ContentItem | RedirectItem | None]:
        resolved_url = url
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = client.fetch(url)
            resolved_url = str(response.url)

            dom = LexborHTMLParser(response.text)

            # Determine the appropriate parser for the content
            parser = None
            for p in self.parsers:
                if p.can_parse(resolved_url, dom):
                    parser = p
                    break

            if parser is None:
                self.logger.warning(f"No suitable parser found for {resolved_url}")
                return None

            self.logger.info(f"Using parser: {parser.__class__.__name__}")
            yield from parser.parse(resolved_url, dom)

        except Exception as e:
            self.logger.error(f"Failed to crawl {resolved_url}: {e}")
            return None
