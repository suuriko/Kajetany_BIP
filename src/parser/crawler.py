import logging
import time

import pandas as pd

from crawler.http_client import HttpClient
from crawler.parser import BaseParser, BipNadarzynParser
from models.elements import Elements

logger = logging.getLogger("crawler")


class Crawler:
    def __init__(self, urls_with_parsers: list[tuple[str, BaseParser]]):
        self.logger = logging.getLogger("parser")
        self.i = 0
        self.urls_with_parsers = urls_with_parsers

    def crawl(self, past_data: pd.DataFrame) -> pd.DataFrame:
        new_data = pd.DataFrame(columns=[Elements.model_fields.keys()])

        with HttpClient() as client:
            for list_url, parser in self.urls_with_parsers:
                r = client.fetch(list_url)
                for item in parser.parse_list(r.text, str(r.url), client):
                    if item is None:
                        continue

                    if not past_data.empty and item.url in past_data["url"].values:
                        continue
                    else:
                        logger.info("New data added")
                        new_row = pd.DataFrame.from_records([item.__dict__])

                        if new_data.empty:
                            new_data = new_row.copy()
                        else:
                            new_data = pd.concat([new_data, new_row], ignore_index=True)

                    time.sleep(1.5)

        return new_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = Crawler([("https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia", BipNadarzynParser())])
    crawler.crawl(pd.DataFrame(columns=[Elements.model_fields.keys()]))
