import redis
import json
import logging
from typing import Dict, Any
from backend.config import settings

logger = logging.getLogger("documind.services.queue")

class QueueManager:
    """
    SECTION 8.1: EVENT-DRIVEN QUEUE MANAGER
    Abstracts the message broker (Redis/Kafka) for the Data Pipeline.
    """
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.stream_name = "documind_events"

    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Publishes an event to the stream for async processing.
        """
        event = {
            "type": event_type,
            "data": payload
        }
        try:
            # We use Redis Streams for v2 event-driven architecture
            self.redis_client.xadd(self.stream_name, {"json": json.dumps(event)})
            logger.info(f"Published {event_type} to stream.")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

class EventConsumer:
    """
    Main loop for consuming events from the stream (The Microservice Worker).
    """
    def __init__(self, service_instance):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.stream_name = "documind_events"
        self.service = service_instance
        self.group_name = "data_update_group"
        self._setup_consumer_group()

    def _setup_consumer_group(self):
        try:
            self.redis_client.xgroup_create(self.stream_name, self.group_name, id='0', mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "already exists" not in str(e):
                raise e

    def listen(self):
        """Infinite loop to process events."""
        logger.info(f"Data Update microservice listening on {self.stream_name}...")
        while True:
            try:
                # Read from group
                messages = self.redis_client.xreadgroup(self.group_name, "consumer_1", {self.stream_name: ">"}, count=1, block=5000)
                if not messages: continue
                
                for stream, msg_list in messages:
                    for msg_id, payload in msg_list:
                        raw_event = json.loads(payload[b'json'])
                        
                        # Process using the DataUpdateService
                        success = self.service.process_event(raw_event["type"], raw_event["data"])
                        
                        if success:
                            # Acknowledge message
                            self.redis_client.xack(self.stream_name, self.group_name, msg_id)
            except Exception as e:
                logger.error(f"Consumer Error: {e}")
