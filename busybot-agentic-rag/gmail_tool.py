import smtplib

# secure socket layer
import ssl


# to build email structure use mimetext
from email.mime.text import MIMEText

# to use app password form .env file
from dotenv import load_dotenv

import os

load_dotenv()


def send_email(receiver_email, subject, message):

    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(message)

    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=context
    ) as server:

        server.login(
            sender_email,
            password.replace(" ", "")
        )

        server.sendmail(
            sender_email,
            receiver_email,
            msg.as_string()
        )

    return {
        "status": "success"
    }

