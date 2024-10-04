
from notificador import Notification, NotificationService
from elasticsearch import Elasticsearch
from notificadorConfig import notification_service
from logger import logger
import dotenv
import os

class IndexMonitor:
    def __init__(self, elasticsearch_client, notification_service: NotificationService, index_name):
        self.elasticsearch_client = elasticsearch_client
        self.notification_service = notification_service
        self.index_name = index_name

    def find_non_processed_alerts(self) -> list:
        query = {
                    "query": {
                        "term": {
                        "processed": False
                        } 
                    }
                }
                
        response = self.elasticsearch_client.search(index=self.index_name, body=query)
        results = response["hits"]["hits"]
        logger.info(f"Found {len(results)} non-processed alerts")
        return results
    
    def mark_as_processed(self, alert_id) -> None:
        logger.debug(f"Marking alert {alert_id} as processed")
        try:
            self.elasticsearch_client.update(
                index=self.index_name,
                id=alert_id,
                body={
                    "doc": {
                        "processed": True
                    }
                }
            )
            logger.info(f"Alert {alert_id} marked as processed successfully")
        except Exception as e:
            logger.error(f"Failed to mark alert {alert_id} as processed: {str(e)}")


    def build_message(self, alerts: list) -> Notification:
        subject = f"Alerts for {self.index_name}"
        message = ""
        for alert in alerts:
            fields = alert["_source"]["data"]
            message += f"Alert on timestamp {alert['_source']['timestamp']}: \n" + [f"{key}: {value}" for key, value in fields.items()].join("\n") + "/n"
        return Notification(message, subject)

    def monitor(self) -> None:
        alerts = self.find_non_processed_alerts()
        if alerts:
            notification = self.build_message(alerts)
            try:
                self.notification_service.send_notification(notification)
            except RuntimeError:
                logger.error("Failed to send notification, alerts will not be marked as processed")
                return
            for alert in alerts:
                self.mark_as_processed(alert["_id"])
            logger.info("Notification sent successfully")
        else:
            logger.info("No alerts to send")



def main() -> None:
    # Set up Elasticsearch client
    dotenv.load_dotenv(override=True)
    es_user = os.getenv("ELASTICSEARCH_USERNAME")
    es_pass = os.getenv("ELASTICSEARCH_PASSWORD")
    es_url = os.getenv("ELASTICSEARCH_URL")
    logger.info(f"Connecting to Elasticsearch at {es_url}")
    es_client = Elasticsearch(
        [es_url],
        timeout=1000,
        basic_auth=(es_user, es_pass),
        verify_certs=False
    )


    # Create and run index monitor
    index_monitor = IndexMonitor(es_client, notification_service, os.getenv("ELASTICSEARCH_INDEX_NAME"))
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