

class IndexMonitor:
    def __init__(self, elasticsearch_client, notification_service: NotificationService, index_name):
        self.elasticsearch_client = elasticsearch_client
        self.notification_service = notification_service
        self.index_name = index_name

    def find_non_processed_alerts(self) -> list:
        query = f"GET /{self.index_name}/_search" + """
                    {
                    "query": {
                        "match": {
                        "processed": "false"
                        } 
                    }
                    }
                """
        response = self.elasticsearch_client.search(query)
        results = response["hits"]["hits"]
        return results
    
    def mark_as_processed(self, alert_id) -> None:
        query = f"POST /{self.index_name}/_update/{alert_id}" + """
                    {
                    "doc": {
                        "processed": true
                    }
                    }
                """
        self.elasticsearch_client.update(query)


    def build_message(self, alerts: list) -> Notification:
        subject = f"Alerts for {self.index_name}"
        message = ""
        for alert in alerts:
            message += f"Alert: {alert['_source']['data']['metric']} on {alert['_source']['data']['mount_point']} with value {alert['_source']['data']['value']}\n"
        return Notification(message, subject)

    def monitor(self) -> None:
        alerts = self.find_non_processed_alerts()
        if alerts:
            notification = self.build_message(alerts)
            self.notification_service.send_notification(notification)
            for alert in alerts:
                self.mark_as_processed(alert["_id"])



def main() -> None:
    # Set up Elasticsearch client
    es_client = Elasticsearch("http://172.16.0.28:9200")

    # Set up SMTP client
    smtp_client = smtplib.SMTP('smtp.example.com', 587)
    smtp_client.starttls()
    smtp_client.login('username', 'password')

    # Set up Slack client
    slack_client = WebClient(token="your-slack-token")

    # Create notification methods
    email_notification = EmailNotification(smtp_client, "admin@example.com")
    slack_notification = SlackNotification(slack_client, "#alerts")

    # Create notification service
    notification_service = NotificationService([email_notification, slack_notification])

    # Create and run index monitor
    index_monitor = IndexMonitor(es_client, notification_service, "test_alerts")
    index_monitor.monitor()

    # Clean up
    smtp_client.quit()


if __name__ == "__main__":
    main()



# example document
# {
#         "_index": "test_alerts",
#         "_id": "9To8FpIBnVJg0huKjYrf",
#         "_score": 0.18232156,
#         "_source": {
#           "timestamp": "2024-09-21T20:18:37.104Z",
#           "processed": false,
#           "data": {
#             "mount_point": "/mnt/volumen",
#             "metric": "system.filesystem.used.pct",
#             "value": "82.3%"
#           }
#         }
#       }