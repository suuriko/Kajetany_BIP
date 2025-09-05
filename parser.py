
import logging
import re, time
from datetime import datetime
from typing import Union
import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import pandas as pd

from elements import Elements

KAJETANY_RE = re.compile(r"\bKajetan\w*\b", re.IGNORECASE)
LIST_URLS = [
    "https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia",
    # "https://bip.nadarzyn.pl/975,procedury-planistyczne-w-toku"
    # dodaj inne, jeśli chcesz
]
HEADERS = {"User-Agent": "KajetanyWatcher/1.0 (+you@example.com)"}

logger = logging.getLogger("parser")


def fetch(client, url):
    r = client.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r

def extract_date(text: str):
    match = re.search(r'\b(\d{2}\.\d{2}\.\d{4})\b', text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%d.%m.%Y").date()
        except ValueError:
            return None
    return None

def parse_list(html, base_url: str = "https://bip.nadarzyn.pl/73%2Ckomunikaty-i-ogloszenia"):
    # dopasuj do realnego markupu tej sekcji BIP
    # tu przykład: szukamy linków z tytułami
    dom = HTMLParser(html)
    for item in dom.css("#PageContent div.obiekt"):
        if "Kajetan" in item.text():
            title = item.css_first("h3").text()
            for a in item.css("a"):  # zawęź selektor po rozpoznaniu drzewa
                href = a.attributes.get("href", "")
                text = (a.text() or "").strip()
                if not href or not text:
                    continue
                full_url = urljoin(base_url, href)   # <— zamiast httpx.URL(..., base=...)
                logger.info(f"Found link in list: \n{title} \n -> {text} \n  -> {full_url}")
                
                yield Elements(
                        main_title=title,
                        title=text,
                        url=full_url,
                        published_at=extract_date(title)
                )

def html_has_kajetany(text):
    return bool(KAJETANY_RE.search(text))

def parse(past_data: pd.DataFrame) -> Union[pd.DataFrame, None]:

    new_data = pd.DataFrame(columns=[Elements.model_fields.keys()])
    with httpx.Client(follow_redirects=True) as client:
        for list_url in LIST_URLS:
            r = fetch(client, list_url)
            for item in parse_list(r.text, str(r.url)):
                if not past_data.empty and item.url in past_data["url"].values:
                    continue
                else:
                    logger.info(f"New data added")
                    new_row = pd.DataFrame.from_records([item.__dict__])

                    if new_data.empty:
                        new_data = new_row.copy()
                    else:
                        new_data = pd.concat([new_data, new_row], ignore_index=True)

                time.sleep(1.5)

    return new_data