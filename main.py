import logging

import pandas as pd

from src.crawler.nadarzyn_bip.crawler import Crawler
from src.crawler.nadarzyn_bip.parser import (
    ArticleAttachmentParser,
    ArticleBriefParser,
    ArticleParser,
    FullArticleParser,
    ListAttachmentParser,
    SearchPageConfiguratorParser,
    SearchPageResultsParser,
)
from src.html_generator import HTMLGenerator
from src.mail_delivery_service import send_to_group
from src.models.elements import ContentItem

RESULTS_FILE = "items.csv"

logger = logging.getLogger("main")


def read_past_csv():
    try:
        return pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[ContentItem.model_fields.keys()])


def run():
    past_data = read_past_csv()
    crawler = Crawler(
        base_url="https://bip.nadarzyn.pl/redir,szukaj?szukaj_wyniki=1&szukaj=kajetany&szukaj_tryb=0&szukaj_aktualnosci_data_od=&szukaj_aktualnosci_data_do=&szukaj_kalendarium_data_od=&szukaj_kalendarium_data_do=&szukaj_data_wybor=1m&szukaj_data_od=&szukaj_data_do=&szukaj_limit=100",
        parsers=[
            SearchPageConfiguratorParser(),
            SearchPageResultsParser(),
            ArticleBriefParser(),
            ArticleParser(),
            ArticleAttachmentParser(),
            ListAttachmentParser(),
            FullArticleParser(),
        ],
    )
    new_data = crawler.crawl(past_data)

    # Generate HTML report from all available data
    html_generator = HTMLGenerator()

    if not new_data.empty:
        logger.info(f"New items found! Saving to {RESULTS_FILE}")
        all_data = pd.concat([past_data, new_data], ignore_index=True)
        all_data.to_csv(RESULTS_FILE, index=False)

        # Generate HTML report with new items count
        html_output = html_generator.generate_from_csv(csv_path=RESULTS_FILE, output_path="gh-pages/index.html")
        logger.info(f"HTML report generated: {html_output}")

        send_to_group(new_data)
        logger.info("Email sent!")
    else:
        logger.info("No new items found.")

        # Still generate HTML report from existing data
        if not past_data.empty:
            html_output = html_generator.generate_from_csv(csv_path=RESULTS_FILE, output_path="gh-pages/index.html")
            logger.info(f"HTML report updated: {html_output}")
        else:
            logger.info("No data available for HTML report.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s:%(name)s]  %(message)s")
    run()
