import logging

import pandas as pd

from src.crawler.crawler import Crawler
from src.crawler.parser import BipNadarzynParser
from src.mail_delivery_service import send_to_group
from src.models.elements import Elements

RESULTS_FILE = "items.csv"

logger = logging.getLogger("main")


def read_past_csv():
    try:
        return pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[Elements.model_fields.keys()])


def run():
    past_data = read_past_csv()
    crawler = Crawler(
        [
            ("https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia", BipNadarzynParser),
            # ("https://bip.nadarzyn.pl/975,procedury-planistyczne-w-toku", AnotherParser()),
        ]
    )
    new_data = crawler.crawl(past_data)

    if not new_data.empty:
        logger.info(f"New items found! Saving to {RESULTS_FILE}")
        all_data = pd.concat([past_data, new_data], ignore_index=True)
        all_data.to_csv(RESULTS_FILE, index=False)

        send_to_group(new_data)


if __name__ == "__main__":
    run()
