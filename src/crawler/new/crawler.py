import logging
import time
from typing import Generator

import pandas as pd
from selectolax.lexbor import LexborHTMLParser

from src.crawler.http_client import HttpClient
from src.crawler.new.base_parser import BaseParser
from src.crawler.new.parser import (
    ArticleAttachmentParser,
    ArticleParser,
    SearchPageConfiguratorParser,
    SearchPageResultsParser,
)
from src.models.elements import ContentItem, RedirectItem


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

    def crawl(self, past_data: pd.DataFrame) -> pd.DataFrame:
        """Crawl all configured URLs and return new items.

        Args:
            past_data: DataFrame containing previously found items

        Returns:
            DataFrame containing newly found items
        """
        new_items = []
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
                    if self._is_duplicate(item, past_data):
                        self.logger.info(f"Item already exists: {item.title}")
                        continue

                    merged_item = item.merge_with_redirect(item_to_crawl)

                    print("New item found:\n", merged_item)
                    new_items.append(merged_item)

                time.sleep(1.5)  # Be respectful to the server

        return pd.DataFrame(new_items) if new_items else pd.DataFrame(columns=list(ContentItem.model_fields.keys()))

    def _is_duplicate(self, item: ContentItem, past_data: pd.DataFrame) -> bool:
        """Check if item already exists in past data."""
        return not past_data.empty and item.url in past_data["url"].values

    def crawl_url(self, url: str, client: HttpClient) -> Generator[ContentItem | RedirectItem | None]:
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = client.fetch(url)

            dom = LexborHTMLParser(response.text)

            # Determine the appropriate parser for the content
            parser = None
            for p in self.parsers:
                if p.can_parse(url, dom):
                    parser = p
                    break

            if parser is None:
                self.logger.warning(f"No suitable parser found for {url}")
                return None

            self.logger.info(f"Using parser: {parser.__class__.__name__}")
            yield from parser.parse(url, dom)

        except Exception as e:
            self.logger.error(f"Failed to crawl {url}: {e}")
            raise e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s:%(name)s]  %(message)s")
    crawler = Crawler(
        base_url="https://bip.nadarzyn.pl/redir,szukaj?szukaj_wyniki=1&szukaj=kajetany&szukaj_tryb=0&szukaj_aktualnosci_data_od=&szukaj_aktualnosci_data_do=&szukaj_kalendarium_data_od=&szukaj_kalendarium_data_do=&szukaj_data_wybor=7d&szukaj_data_od=2024-03-01&szukaj_data_do=2024-03-31&szukaj_limit=100",
        parsers=[SearchPageConfiguratorParser(), SearchPageResultsParser(), ArticleParser(), ArticleAttachmentParser()],
    )
    crawler.crawl(pd.DataFrame(columns=[ContentItem.model_fields.keys()]))
