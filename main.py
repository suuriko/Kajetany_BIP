import logging
import os

import pandas as pd
from dotenv import load_dotenv

from src.crawler.nadarzyn_bip.crawler import Crawler
from src.crawler.nadarzyn_bip.parser import (
    ArticleAttachmentParser,
    ArticleBriefParser,
    ArticleParser,
    AuctionAttachmentParser,
    FullArticleParser,
    ListAttachmentParser,
    SearchPageConfiguratorParser,
    SearchPageResultsParser,
)
from src.html_generator import HTMLGenerator
from src.item_repository import ItemRepository
from src.mail_service import MailService
from src.models import ContentItem

# Load environment variables from .env file
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")  # Gmail address
SMTP_PASS = os.getenv("SMTP_PASS")  # App Password (16 characters)
TO_GROUP = os.getenv("TO_GROUP")  # Target group email address

RESULTS_FILE = "items.csv"

logger = logging.getLogger("main")


def read_past_csv():
    try:
        return pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[*ContentItem.model_fields.keys()])


def run():
    if not SMTP_USER or not SMTP_PASS or not TO_GROUP:
        raise RuntimeError("SMTP_USER, SMTP_PASS and TO_GROUP environment variables must be set and non-empty.")

    mail_service = MailService(SMTP_USER, SMTP_PASS)
    html_generator = HTMLGenerator()

    past_data = read_past_csv()
    item_repository = ItemRepository.from_dataframe(past_data)

    crawler = Crawler(
        base_url="https://bip.nadarzyn.pl/redir,szukaj?szukaj_wyniki=1&szukaj=kajetany&szukaj_tryb=0&szukaj_aktualnosci_data_od=&szukaj_aktualnosci_data_do=&szukaj_kalendarium_data_od=&szukaj_kalendarium_data_do=&szukaj_data_wybor=1m&szukaj_data_od=&szukaj_data_do=&szukaj_limit=100",
        parsers=[
            SearchPageConfiguratorParser(),
            SearchPageResultsParser(),
            AuctionAttachmentParser(),
            ArticleBriefParser(),
            ArticleParser(),
            ArticleAttachmentParser(),
            ListAttachmentParser(),
            FullArticleParser(),
        ],
    )
    crawled_items = crawler.crawl()
    new_data = [item for item in crawled_items if not item_repository.exists(item)]

    if len(new_data) > 0:
        logger.info(f"New items found! Saving to {RESULTS_FILE}")
        item_repository.add_items(new_data)
        item_repository.to_dataframe().to_csv(RESULTS_FILE, index=False)

        html_output = html_generator.generate_from_csv(csv_path=RESULTS_FILE, output_path="gh-pages/index.html")
        logger.info(f"HTML report generated: {html_output}")

        email_content = html_generator.generate_email_content(new_data)
        mail_service.send_to_group(TO_GROUP, email_content)
        logger.info(f"Email sent to {TO_GROUP} with {len(new_data)} new items.")
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
