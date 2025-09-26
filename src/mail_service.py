import datetime
import smtplib
import ssl
from email.message import EmailMessage


class MailService:
    def __init__(self, user: str, password: str):
        if not user or not password:
            raise ValueError("User and password must be set.")
        self.user = user
        self.password = password

    def send_to_group(self, to_group: str, email_content: str) -> None:
        date = datetime.date.today().strftime("%d.%m.%Y")

        msg = EmailMessage()
        msg["Subject"] = "[BIP Bot] Nowości dla Kajetan w BIP Nadarzyn - " + date
        msg["From"] = self.user
        msg["To"] = to_group
        msg.set_content(email_content, subtype="html")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
            s.login(self.user, self.password)
            s.send_message(msg)
