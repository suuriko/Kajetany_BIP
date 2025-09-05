import logging
import re, time
from datetime import datetime
import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import pandas as pd

from elements import Elements
from parser import parse


RESULTS_FILE = "items.csv"

logger = logging.getLogger("main")


def read_past_csv():
    try:
        return pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[Elements.model_fields.keys()])


def run():
    past_data = read_past_csv()
    new_data = parse(past_data) 

    if not new_data.empty:
        logger.info(f"New items found! Saving to {RESULTS_FILE}")
        all_data = pd.concat([past_data, new_data], ignore_index=True)
        all_data.to_csv(RESULTS_FILE, index=False)

if __name__ == "__main__":
    run()