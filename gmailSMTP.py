import dotenv
import os
import smtplib
from email.mime.text import MIMEText

class SMTPGMail:
    def __init__(self):
        self.smtp_client = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp_client.starttls()
        self.smtp_client.login(os.getenv('GMAIL_USERNAME'), os.getenv('GMAIL_PASSWORD'))

    def send_message(self, message: MIMEText):
        self.smtp_client.send_message(message)
