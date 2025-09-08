import os
import smtplib
import ssl
from email.message import EmailMessage

import pandas as pd

SMTP_USER = os.getenv("SMTP_USER")  # Twój Gmail
SMTP_PASS = os.getenv("SMTP_PASS")  # App Password (16 znaków)
TO_GROUP = os.getenv("TO_GROUP", "suuriko@gmail.com")


def generate_email_content_html(new_entries: pd.DataFrame):
    if new_entries.empty:
        return None

    grouped = new_entries.groupby("main_title")["url"].apply(list).reset_index()

    email_html = """
<html><body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f8f9fa; padding: 20px;">
<div style="max-width: 650px; margin: auto; background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <h2 style="color: #2c3e50; text-align: center;"> Nowe wpisy na stronie BIP Nadarzyn</h2>
    <p>Drodzy Mieszkańcy Kajetan,</p>
    <p>Na stronie <b>BIP Nadarzyn</b> pojawiły się nowe wpisy:</p>"""

    for _, row in grouped.iterrows():
        email_html += f"""
        <h4 style="margin-bottom: 15px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;">{row['main_title']}</h4>
        <ul style="margin: 5px 0 0 20px; padding: 0;">"""
        for link in row["url"]:
            email_html += f"""
            <li style="margin-bottom: 5px;">
                <a href="{link}" style="color: #007bff; text-decoration: none;">{link}</a>
            </li>"""
        email_html += """
        </ul>"""

    email_html += """
    <p style="margin-top: 25px;">Zachęcamy do zapoznania się ze szczegółami.</p>
    <p style="color: #555;">Pozdrawiamy,<br><b>Bot Kajetany </b></p>
    <hr style="border: none; border-top: 1px solid #ddd; margin-top: 20px;">
    <p style="font-size: 12px; color: #888; text-align: center;">Wiadomość wygenerowana automatycznie. Prosimy na nią nie odpowiadać.</p>
</div>
</body></html>"""
    return email_html


def send_to_group(data: pd.DataFrame):
    email_content = generate_email_content_html(data)

    msg = EmailMessage()
    msg["Subject"] = "[BIP Bot] Nowe wpisy dla Kajetan w BIP Nadarzyn"
    msg["From"] = SMTP_USER
    msg["To"] = TO_GROUP
    msg.set_content(email_content, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

    print(f"Email sent to {TO_GROUP} with {len(data)} new entries.")
