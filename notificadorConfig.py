from notificador import NotificationService, EmailNotification, SlackNotification
from gmailSMTP import SMTPGMail
import dotenv
import os
from slack_sdk import WebClient

dotenv.load_dotenv()

###############
# Config
###############


email_sender = os.getenv("GMAIL_USERNAME")
email_password = os.getenv("GMAIL_PASSWORD")
email_receiver = "mtorrente@dblandit.com"
slack_channel = "#code"
#smtp_client = SMTPGMail(email_sender, email_password)
slack_client = WebClient(token=os.getenv("SLACK_TOKEN"))

################


notification_methods = [
    #EmailNotification(smtp_client, email_receiver),
    SlackNotification(slack_client, slack_channel)
]        

notification_service = NotificationService(notification_methods)





