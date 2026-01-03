import pika
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EventBus:
    """Event bus for inter-service communication using RabbitMQ"""

    def __init__(self, rabbitmq_url: Optional[str] = None):
        self.rabbitmq_url = rabbitmq_url or os.getenv(
            'RABBITMQ_URL',
            'amqp://guest:guest@localhost:5672/'
        )
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

        # Declare exchanges on initialization
        self._ensure_connection()
        self._declare_exchanges()

    def _ensure_connection(self):
        """Ensure RabbitMQ connection is established"""
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(self.rabbitmq_url)
                )
                self.channel = self.connection.channel()
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    def _declare_exchanges(self):
        """Declare all required exchanges"""
        exchanges = [
            'identity', 'audit', 'project', 'accounting',
            'hr', 'sales', 'notification'
        ]

        for exchange in exchanges:
            try:
                self.channel.exchange_declare(
                    exchange=exchange,
                    exchange_type='topic',
                    durable=True
                )
                logger.debug(f"Declared exchange: {exchange}")
            except Exception as e:
                logger.error(f"Failed to declare exchange {exchange}: {e}")

    def publish(self, exchange: str, routing_key: str, event_data: Dict[str, Any]):
        """Publish event to message bus"""
        self._ensure_connection()

        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': routing_key,
            'timestamp': datetime.now().isoformat(),
            'data': event_data,
            'correlation_id': event_data.get('correlation_id'),
        }

        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(event),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json',
                    message_id=event['event_id'],
                    timestamp=int(datetime.now().timestamp())
                )
            )
            logger.info(f"Published event: {routing_key} to {exchange}")
        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            raise

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
            except Exception as e:
                logger.error(f"Error closing RabbitMQ connection: {e}")

# Global event bus instance
event_bus = EventBus()</content>
<parameter name="filePath">backend/shared/event_bus.py