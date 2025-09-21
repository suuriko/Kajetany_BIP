import logging
import time
from typing import Sequence

import pandas as pd

from src.crawler.http_client import HttpClient
from src.crawler.parsers.base_parser import BaseParser
from src.crawler.parsers.bip_nadarzyn_list_parser import BipNadarzynListParser
from src.models.elements import Elements


class Crawler:
    """Orchestrates web crawling using multiple parsers.

    Manages HTTP client lifecycle and coordinates parsing of multiple URLs
    with their respective parser implementations.
    """

    def __init__(self, urls_with_parsers: Sequence[tuple[str, type[BaseParser]]]) -> None:
        """Initialize crawler with URL-parser mappings.

        Args:
            urls_with_parsers: List of (URL, parser_class) tuples
        """
        self.logger = logging.getLogger("crawler")
        self.urls_with_parsers = urls_with_parsers

    def crawl(self, past_data: pd.DataFrame) -> pd.DataFrame:
        """Crawl all configured URLs and return new items.

        Args:
            past_data: DataFrame containing previously found items

        Returns:
            DataFrame containing newly found items
        """
        new_items = []

        with HttpClient() as client:
            for list_url, parser_class in self.urls_with_parsers:
                try:
                    response = client.fetch(list_url)
                    parser = parser_class(http_client=client, base_url=list_url)

                    for item in parser.parse_list(response.text):
                        if item is None:
                            continue

                        if self._is_duplicate(item, past_data):
                            continue

                        self.logger.info(f"New item found: {item.title}")
                        new_items.append(item.__dict__)
                        time.sleep(1.5)  # Be respectful to the server

                except Exception as e:
                    self.logger.error(f"Failed to crawl {list_url}: {e}")
                    continue

        return pd.DataFrame(new_items) if new_items else pd.DataFrame(columns=list(Elements.model_fields.keys()))

    def _is_duplicate(self, item: Elements, past_data: pd.DataFrame) -> bool:
        """Check if item already exists in past data."""
        return not past_data.empty and item.url in past_data["url"].values


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = Crawler([("https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia", BipNadarzynListParser)])
    crawler.crawl(pd.DataFrame(columns=[Elements.model_fields.keys()]))
