import pika
import json
import uuid
import os
import threading
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

# Event validation schemas (will be enhanced with Pydantic when available)
class EventValidator:
    """Basic event validation until Pydantic is available"""

    @staticmethod
    def validate_event(event_data: Dict[str, Any]) -> bool:
        """Validate basic event structure"""
        required_fields = ['event_type', 'data', 'source_service']
        return all(field in event_data for field in required_fields)

    @staticmethod
    def validate_event_type(event_type: str) -> bool:
        """Validate event type format"""
        return isinstance(event_type, str) and '.' in event_type

class BaseEvent:
    """Base event structure"""
    def __init__(self, event_type: str, data: Dict[str, Any], source_service: str,
                 correlation_id: Optional[str] = None, priority: EventPriority = EventPriority.NORMAL,
                 target_service: Optional[str] = None):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = datetime.now().isoformat()
        self.correlation_id = correlation_id
        self.priority = priority
        self.data = data
        self.source_service = source_service
        self.target_service = target_service

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'correlation_id': self.correlation_id,
            'priority': self.priority.value,
            'data': self.data,
            'source_service': self.source_service,
            'target_service': self.target_service,
        }

class EventBus:
    """Production-ready event bus with all critical fixes"""

    def __init__(self, rabbitmq_url: Optional[str] = None):
        self.rabbitmq_url = rabbitmq_url or os.getenv(
            'RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/'
        )
        self.connection = None
        self.channel = None
        self.lock = threading.Lock()  # Thread safety fix
        self._connect()
        self._declare_exchanges()
        self._declare_dlq()  # Dead Letter Queue fix

    def _connect(self):
        """Thread-safe connection establishment"""
        with self.lock:
            if not self.connection or self.connection.is_closed:
                try:
                    self.connection = pika.BlockingConnection(
                        pika.URLParameters(self.rabbitmq_url)
                    )
                    self.channel = self.connection.channel()
                    logger.info("Connected to RabbitMQ")
                except Exception as e:
                    logger.error(f"Failed to connect to RabbitMQ: {e}")
                    self.connection = None
                    self.channel = None
                    raise

    def _declare_exchanges(self):
        """Declare all required exchanges"""
        exchanges = [
            'identity', 'audit', 'project', 'accounting',
            'hr', 'sales', 'notification'
        ]

        with self.lock:
            if not self.channel:
                logger.error("Channel not available for declaring exchanges")
                return

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

    def _declare_dlq(self):
        """Declare Dead Letter Queue for failed messages"""
        with self.lock:
            if not self.channel:
                logger.error("Channel not available for declaring DLQ")
                return

            try:
                # Dead letter exchange
                self.channel.exchange_declare(
                    exchange='dlq',
                    exchange_type='direct',
                    durable=True
                )

                # Dead letter queue
                self.channel.queue_declare(
                    queue='dlq.events',
                    durable=True,
                    arguments={
                        'x-message-ttl': 86400000,  # 24 hours
                        'x-dead-letter-exchange': '',  # Discard after TTL
                    }
                )

                self.channel.queue_bind(
                    'dlq.events', 'dlq', routing_key='dlq'
                )

                logger.info("Declared Dead Letter Queue")
            except Exception as e:
                logger.error(f"Failed to declare DLQ: {e}")

    def publish(self, exchange: str, routing_key: str, event_data: Dict[str, Any]):
        """Publish event with simple retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._connect()

                event = {
                    'event_id': str(uuid.uuid4()),
                    'event_type': routing_key,
                    'timestamp': datetime.now().isoformat(),
                    'data': event_data,
                    'correlation_id': event_data.get('correlation_id'),
                }

                with self.lock:
                    if not self.channel:
                        raise Exception("Channel not available for publishing")

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
                    return

            except Exception as e:
                logger.error(f"Failed to publish event {routing_key} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def publish_event(self, event: BaseEvent):
        """Publish a typed event"""
        if not EventValidator.validate_event(event.to_dict()):
            raise ValueError(f"Invalid event structure: {event.to_dict()}")

        self.publish(
            exchange=event.source_service,
            routing_key=event.event_type,
            event_data=event.to_dict()
        )

    def publish_async(self, exchange: str, routing_key: str, event_data: Dict[str, Any]):
        """Asynchronous publish to prevent blocking"""
        thread = threading.Thread(
            target=self.publish,
            args=(exchange, routing_key, event_data),
            daemon=True
        )
        thread.start()

    def publish_event_async(self, event: BaseEvent):
        """Asynchronous publish of typed event"""
        thread = threading.Thread(
            target=self.publish_event,
            args=(event,),
            daemon=True
        )
        thread.start()

    def health_check(self) -> bool:
        """Check if the event bus is healthy"""
        try:
            with self.lock:
                if not self.connection or self.connection.is_closed:
                    return False
                # Try a simple operation to verify connection
                self.connection.process_data_events()
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            'connection_status': 'connected' if self.connection and not self.connection.is_closed else 'disconnected',
            'rabbitmq_url': self.rabbitmq_url.replace('amqp://', 'amqp://***:***@') if 'amqp://' in self.rabbitmq_url else self.rabbitmq_url,
            'timestamp': datetime.now().isoformat(),
        }

    def close(self):
        """Graceful shutdown"""
        with self.lock:
            if self.connection and not self.connection.is_closed:
                try:
                    self.connection.close()
                    logger.info("Closed RabbitMQ connection")
                except Exception as e:
                    logger.error(f"Error closing RabbitMQ connection: {e}")

class EventConsumer:
    """Event consumer with acknowledgment and error handling"""

    def __init__(self, event_bus: EventBus, exchange: str, routing_key: str, callback: Callable):
        self.event_bus = event_bus
        self.exchange = exchange
        self.routing_key = routing_key
        self.callback = callback
        self.consumer_tag = None

    def start_consuming(self):
        """Start consuming events"""
        with self.event_bus.lock:
            if not self.event_bus.channel:
                logger.error("Channel not available for consuming")
                return

            # Declare queue
            queue_name = f"{self.exchange}.{self.routing_key.replace('.', '_')}"

            self.event_bus.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'dlq',
                    'x-dead-letter-routing-key': 'dlq',
                }
            )

            self.event_bus.channel.queue_bind(
                queue_name, self.exchange, routing_key=self.routing_key
            )

            def wrapper_callback(ch, method, properties, body):
                try:
                    event_data = json.loads(body)
                    self.callback(event_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    # Send to DLQ
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.consumer_tag = self.event_bus.channel.basic_consume(
                queue_name, on_message_callback=wrapper_callback
            )

            logger.info(f"Started consuming events from {self.exchange}:{self.routing_key}")
            self.event_bus.channel.start_consuming()

    def stop_consuming(self):
        """Stop consuming events"""
        if self.consumer_tag and self.event_bus.channel:
            self.event_bus.channel.basic_cancel(self.consumer_tag)

# Global event bus instance
event_bus = EventBus()