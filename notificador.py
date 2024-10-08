from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from logger import logger

class Notification:
    def __init__(self, body, subject):
        self.body = body
        self.subject = subject

class NotificationMethod(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> None:
        pass

class EmailNotification(NotificationMethod):
    def __init__(self, SMTPClient, recipient):
        self.SMTPClient = SMTPClient
        self.recipient = recipient

    def send(self, notification: Notification) -> None:
        msg = MIMEText(notification.body)
        msg['Subject'] = notification.subject
        msg['From'] = "alerts@example.com"
        msg['To'] = self.recipient
        self.SMTPClient.send_message(msg)
        logger.info(f"Email notification sent to {self.recipient}")

class SlackNotification(NotificationMethod):
    def __init__(self, SlackClient, channel):
        self.SlackClient = SlackClient
        self.channel = channel

    def send(self, notification: Notification) -> None:
        self.SlackClient.chat_postMessage(channel=self.channel, text=notification.body)
        logger.info(f"Slack notification sent to channel {self.channel}")

class NotificationService:
    def __init__(self, notification_methods: list[NotificationMethod]):
        self.notification_methods = notification_methods

    def send_notification(self, notification: Notification) -> None:
        notification_sent = False
        for notification_method in self.notification_methods:
            try:
                notification_method.send(notification)
                notification_sent = True
            except Exception as e:
                logger.error(f"Failed to send notification via {notification_method.__class__.__name__}: {str(e)} for notification: {notification.body}")
        if not notification_sent:
            logger.error("Failed to send notification via any method for notification: {notification.body}")
            raise RuntimeError("Failed to send notification via any method")
