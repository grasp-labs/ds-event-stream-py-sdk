"""
kafka_service.py
KafkaService: Producer and Consumer for DS Kafka Server
"""


from typing import Any, Callable, Optional
from dseventstream.models.event import Event

from confluent_kafka import Producer, Consumer
import json
from dseventstream.kafka.kafka_config import KafkaConfig


class KafkaProducerService:
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer = Producer(self.config.to_dict())

    def send(self, topic: str, event: Event, key: Optional[str] = None):
        """
        Send an event (should be a dataclass from models) to Kafka.
        """
        def delivery_report(err, msg):
            if err is not None:
                print(f"Delivery failed for record {msg.key()}: {err}")
            else:
                print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

        # If event is a dataclass, convert to dict then to JSON
        if hasattr(event, "__dataclass_fields__"):
            value = json.dumps(event.__dict__)
        else:
            value = json.dumps(event)

        self.producer.produce(
            topic,
            value=value,
            key=key,
            callback=delivery_report
        )
        self.producer.flush()


class KafkaConsumerService:
    def __init__(self, config: KafkaConfig, group_id: str):
        self.config = config
        self.group_id = group_id
        consumer_config = self.config.to_dict()
        consumer_config.update({
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        })
        self.consumer = Consumer(consumer_config)

    def consume(self, topic: str, on_message: Callable[[Any], None]):
        self.consumer.subscribe([topic])
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                value = json.loads(msg.value().decode('utf-8'))
                on_message(value)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()


# Helper functions to create Producer and Consumer instances for prod and dev
def create_kafka_producer_prod() -> KafkaProducerService:
    """
    Create a KafkaProducerService instance for production environment.
    """
    config = KafkaConfig(
        bootstrap_servers="kafka-prod:9092",
        username="service-principal",
        password="secret"
    )
    return KafkaProducerService(config=config)

def create_kafka_producer_dev() -> KafkaProducerService:
    """
    Create a KafkaProducerService instance for development environment.
    """
    config = KafkaConfig(bootstrap_servers="localhost:9092")
    return KafkaProducerService(config=config)

def create_kafka_consumer_prod() -> KafkaConsumerService:
    """
    Create a KafkaConsumerService instance for production environment.
    """
    config = KafkaConfig(
        bootstrap_servers="kafka-prod:9092",
        username="service-principal",
        password="secret"
    )
    group_id = "ds-event-stream-prod"
    return KafkaConsumerService(config=config, group_id=group_id)

def create_kafka_consumer_dev() -> KafkaConsumerService:
    """
    Create a KafkaConsumerService instance for development environment.
    """
    config = KafkaConfig(bootstrap_servers="localhost:9092")
    group_id = "ds-event-stream-dev"
    return KafkaConsumerService(config=config, group_id=group_id)
