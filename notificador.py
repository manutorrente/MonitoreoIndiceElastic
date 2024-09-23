from abc import ABC, abstractmethod

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
        self.SMTPClient.send_email(self.recipient, notification.body , notification.subject)


class SlackNotification(NotificationMethod):
    def __init__(self, SlackClient, channel):
        self.SlackClient = SlackClient
        self.channel = channel

    def send(self, notification: Notification) -> None:
        self.SlackClient.send_message(self.channel, notification.body)


class NotificationService:
    def __init__(self, notification_methods: list[NotificationMethod]):
        self.notification_methods = notification_methods

    def send_notification(self, notification: Notification) -> None:
        for notification_method in self.notification_methods:
            notification_method.send(notification)