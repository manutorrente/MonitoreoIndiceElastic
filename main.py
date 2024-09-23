
from notificador import Notification, NotificationService
from elasticsearch import Elasticsearch
from notificadorConfig import notification_service
import dotenv
import os

class IndexMonitor:
    def __init__(self, elasticsearch_client, notification_service: NotificationService, index_name):
        self.elasticsearch_client = elasticsearch_client
        self.notification_service = notification_service
        self.index_name = index_name

    def find_non_processed_alerts(self) -> list:
        query ={
                    "query": {
                        "match": {
                        "processed": False
                        } 
                    }
                }
                
        response = self.elasticsearch_client.search(index=self.index_name, body=query)
        results = response["hits"]["hits"]
        return results
    
    def mark_as_processed(self, alert_id) -> None:
        self.elasticsearch_client.update(
            index=self.index_name,
            id=alert_id,
            body={
                "doc": {
                    "processed": True
                }
            }
        )


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
    dotenv.load_dotenv()
    es_user = os.getenv("ELASTICSEARCH_USERNAME")
    es_pass = os.getenv("ELASTICSEARCH_PASSWORD")
    es_client = Elasticsearch(
        ['https://172.16.0.28:9200'],
        timeout=1000,
        basic_auth=(es_user, es_pass),
        verify_certs=False
    )


    # Create and run index monitor
    index_monitor = IndexMonitor(es_client, notification_service, "test_alerts")
    index_monitor.monitor()

    # Clean up


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