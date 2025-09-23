import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

from src.html_generator import HTMLGenerator
from src.models.elements import ContentItem

# Load environment variables from .env file
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")  # Twój Gmail
SMTP_PASS = os.getenv("SMTP_PASS")  # App Password (16 znaków)
TO_GROUP = os.getenv("TO_GROUP")  # Adres e-mail grupy docelowej


def generate_email_content_html(new_entries: pd.DataFrame) -> Optional[str]:
    """
    Generate HTML email content from pandas DataFrame using Jinja2 template.

    Args:
        new_entries: DataFrame with BIP content items

    Returns:
        HTML email content as string, or None if no entries
    """
    if new_entries.empty:
        return None

    # Convert DataFrame to ContentItem objects
    items = []
    for _, row in new_entries.iterrows():
        try:
            # Convert row to dict and handle NaN values
            item_data = row.to_dict()
            for key, value in item_data.items():
                if pd.isna(value):
                    item_data[key] = None

            item = ContentItem(**item_data)
            items.append(item)
        except Exception as e:
            print(f"Warning: Could not create ContentItem from row: {e}")
            continue

    if not items:
        return None

    # Generate email using HTMLGenerator
    generator = HTMLGenerator()
    return generator.generate_email_content(items)


def send_to_group(data: pd.DataFrame):
    if not SMTP_USER or not SMTP_PASS or not TO_GROUP:
        raise RuntimeError("SMTP_USER, SMTP_PASS, and TO_GROUP environment variables must be set and non-empty.")

    email_content = generate_email_content_html(data)

    msg = EmailMessage()
    msg["Subject"] = "[BIP Bot] Nowe wpisy i aktualizacje dla Kajetan w BIP Nadarzyn"
    msg["From"] = SMTP_USER
    msg["To"] = TO_GROUP
    msg.set_content(email_content, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

    print(f"Email sent to {TO_GROUP} with {len(data)} new entries.")


if __name__ == "__main__":
    items = [
        ContentItem(
            url="https://example.com/1",
            main_title="Ogłoszenie 1",
            title="Ogłoszenie 1",
            description="Opis 1",
            created_at=None,
            published_at=None,
            last_modified_at=None,
        ),
        ContentItem(
            url="https://example.com/2",
            main_title="Ogłoszenie 2",
            title="Ogłoszenie 2",
            description=None,
            created_at=None,
            published_at=None,
            last_modified_at=None,
        ),
        ContentItem(
            url="https://example.com/3",
            main_title="Ogłoszenie 3",
            title="Plik 1",
            description="Opis 2",
            created_at=None,
            published_at=None,
            last_modified_at=None,
        ),
        ContentItem(
            url="https://example.com/4",
            main_title="Ogłoszenie 3",
            title="Plik 2",
            description="Opis 2",
            created_at=None,
            published_at=None,
            last_modified_at=None,
        ),
    ]
    # Example usage
    df = pd.DataFrame(item.model_dump() for item in items)
    html = generate_email_content_html(df)
    if html:
        with open("email_content.html", "w", encoding="utf-8") as f:
            f.write(html)
