"""
File: base.py
Description: Base Kafka producer implementation.
Region: packages/shared

# Example:
#
# producer = KafkaProducer(bootstrap_servers="localhost:9092")
# producer.send_message(topic="events", message=event_stream)
"""

import json
import traceback
from collections.abc import Callable
from typing import Any

from confluent_kafka import KafkaError, Message, Producer
from ds_common_logger_py_lib import Logger
from ds_common_serde_py_lib.errors import SerializationError

from ..errors import ProducerError
from ..models.v1 import EventStream

logger = Logger.get_logger(__name__)


class KafkaProducer:
    """Base Kafka producer for sending pipeline events."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "ds.event.stream.producer",
        # SASL_SSL Authentication (required for production)
        sasl_username: str | None = None,
        sasl_password: str | None = None,
        ssl_ca_location: str = "/etc/ssl/certs/ca-certificates.crt",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Kafka producer.

        Args:
            bootstrap_servers: Kafka broker addresses.
            client_id: Producer client ID.
            sasl_username: SASL username.
            sasl_password: SASL password.
            ssl_ca_location: Location of the SSL CA certificate.
            kwargs: Additional keyword arguments passed to the underlying producer.
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id

        # Producer configuration
        self.config: dict[str, Any] = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
            **kwargs,
        }
        self.config.setdefault("ssl.ca.location", ssl_ca_location)
        if sasl_username and sasl_password:
            self.config.update(
                {
                    "security.protocol": "SASL_PLAINTEXT",
                    "sasl.username": sasl_username,
                    "sasl.password": sasl_password,
                    "sasl.mechanisms": "SCRAM-SHA-512",
                }
            )
        else:
            self.config.update(
                {
                    "security.protocol": "PLAINTEXT",
                }
            )

        # Create producer
        self.producer: Producer = Producer(self.config)

    def send_message(
        self,
        topic: str,
        message: EventStream,
        key: str | None = None,
        callback: Callable[[KafkaError | None, Message], None] | None = None,
    ) -> None:
        """
        Send a message to a topic.

        This method is used to send a message to a topic.
        It will serialize the message to a JSON string and send it to the topic.
        It will also log the message and the key.

        Args:
            topic: Topic to send message to.
            message: Message data to send.
            key: Optional message key.
            callback: Optional callback function invoked on delivery.
        """
        try:
            message_bytes = json.dumps(message.serialize()).encode("utf-8")
            key_bytes = key.encode("utf-8") if key else None

            self.producer.produce(
                topic=topic,
                value=message_bytes,
                key=key_bytes,
                callback=callback or self._callback,
            )

            self.producer.flush(timeout=60.0)

            logger.debug("Kafka message sent", extra={"topic": topic, "key": key})
        except SerializationError as exc:
            logger.error(
                "Failed to serialize message",
                extra={
                    "topic": topic,
                    "error": {
                        "code": "DS_KAFKA_PRODUCER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
            raise exc
        except Exception as exc:
            logger.error(
                "Failed to send kafka message",
                extra={
                    "topic": topic,
                    "error": {
                        "code": "DS_KAFKA_PRODUCER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
            raise ProducerError(
                details={"topic": topic},
            ) from exc

    def _callback(self, err: KafkaError | None, msg: Message) -> None:
        """
        Callback for message delivery reports.

        Args:
            err: Error object.
            msg: Message object.
        """
        if err is not None:
            extra: dict[str, Any] = {
                "error": {
                    "code": "DS_KAFKA_PRODUCER_ERROR",
                    "type": type(err).__name__,
                    "message": str(err),
                    "traceback": traceback.format_exc(),
                },
            }
            extra.update(
                {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                }
            )
            logger.error("Message delivery failed", extra=extra)
        else:
            logger.debug(
                "Message delivered",
                extra={
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                },
            )

    def close(self) -> None:
        """
        Close the producer.

        Returns:
            None
        """
        self.producer.flush(timeout=60.0)
        logger.debug("Producer closed")
