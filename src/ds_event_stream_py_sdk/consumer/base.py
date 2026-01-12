"""
File: base.py
Description: Base Kafka consumer implementation.
Region: packages/shared

# Example:
#
# consumer = KafkaConsumer(bootstrap_servers="localhost:9092", topics=["events"])
# consumer.add_message_handler("events", lambda event: print(event.event_type))
# consumer.start()
"""

import json
import traceback
from collections.abc import Callable
from typing import Any

from confluent_kafka import Consumer, KafkaError, Message
from ds_common_logger_py_lib import Logger
from ds_common_serde_py_lib.errors import DeserializationError

from ..errors import ConsumerError
from ..models.v1 import EventStream

logger = Logger.get_logger(__name__)


class KafkaConsumer:
    """Base Kafka consumer for handling pipeline events."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "ds.event.stream.consumer",
        group_id: str = "ds.event.stream.consumer",
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = False,
        session_timeout_ms: int = 45000,
        topics: list[str] | None = None,
        sasl_username: str | None = None,
        sasl_password: str | None = None,
        ssl_ca_location: str = "/etc/ssl/certs/ca-certificates.crt",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Kafka consumer.

        Args:
            bootstrap_servers: Kafka broker addresses.
            client_id: Consumer client ID.
            group_id: Consumer group ID.
            auto_offset_reset: Offset reset policy.
            enable_auto_commit: Whether to auto-commit offsets.
            session_timeout_ms: Session timeout in milliseconds.
            topics: List of topics to subscribe to.
            sasl_username: SASL username.
            sasl_password: SASL password.
            ssl_ca_location: Location of the SSL CA certificate.
            kwargs: Additional keyword arguments passed to the underlying consumer.
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics or []
        self.consumer: Consumer | None = None
        self.running: bool = False
        self.current_message: Message | None = None

        # Consumer configuration
        self.config: dict[str, Any] = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": enable_auto_commit,
            "session.timeout.ms": session_timeout_ms,
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

        # Message handlers
        self.message_handlers: dict[str, Callable[[EventStream], Any]] = {}

    def add_message_handler(
        self,
        topics: str | list[str],
        handler: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Add a message handler for one or more topics.

        Args:
            topics: Topic name (str) or list of topic names.
            handler: Function to handle messages from these topics.
            *args: Additional positional arguments to pass to the handler.
            **kwargs: Additional keyword arguments to pass to the handler.

        Returns:
            None
        """
        if isinstance(topics, str):
            topics = [topics]

        def wrapper(message: EventStream) -> Any:
            """
            Invoke the configured handler with the message and bound arguments.

            Args:
                message: Event stream message.

            Returns:
                The handler return value.
            """
            return handler(message, *args, **kwargs)

        # Register the handler for all specified topics
        for topic in topics:
            self.message_handlers[topic] = wrapper
            logger.debug("Added message handler", extra={"topic": topic})

    def commit_message(self) -> None:
        """
        Explicitly commit the current message.

        Returns:
            None
        """
        if self.current_message is None or self.consumer is None:
            return
        try:
            self.consumer.commit(self.current_message)
            logger.debug(
                "Message committed successfully",
                extra={
                    "topic": self.current_message.topic(),
                    "partition": self.current_message.partition(),
                    "offset": self.current_message.offset(),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to commit message",
                extra={
                    "topic": self.current_message.topic(),
                    "partition": self.current_message.partition(),
                    "offset": self.current_message.offset(),
                    "error": {
                        "code": "KAFKA_CONSUMER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
            raise ConsumerError(
                details={
                    "topic": self.current_message.topic(),
                    "partition": self.current_message.partition(),
                    "offset": self.current_message.offset(),
                },
            ) from exc

    def start(self) -> None:
        """
        Start consuming messages.

        Returns:
            None
        """
        try:
            # Create consumer
            consumer = Consumer(self.config)
            self.consumer = consumer

            # Subscribe to topics
            consumer.subscribe(
                self.topics,
                on_assign=self._on_assign,
                on_revoke=self._on_revoke,
            )
            logger.debug("Subscribed to topics", extra={"topics": self.topics})

            self.running = True

            # Start consuming
            while self.running:
                try:
                    msg = consumer.poll(timeout=1.0)

                    if msg is None:
                        continue

                    if msg.error():
                        err = msg.error()
                        if err is not None and err.code() == KafkaError._PARTITION_EOF:
                            logger.debug(
                                "Reached end of partition",
                                extra={
                                    "topic": msg.topic(),
                                    "partition": msg.partition(),
                                },
                            )
                        else:
                            logger.error(
                                "Consumer error",
                                extra={
                                    "topic": msg.topic(),
                                    "partition": msg.partition(),
                                    "offset": msg.offset(),
                                    "error": {
                                        "code": "DS_KAFKA_CONSUMER_ERROR",
                                        "type": type(err).__name__ if err is not None else "KafkaError",
                                        "message": str(err) if err is not None else "",
                                        "traceback": traceback.format_exc(),
                                    },
                                },
                            )
                        continue

                    self.current_message = msg
                    self._process_message(msg)

                except KeyboardInterrupt:
                    logger.debug("Received interrupt signal, stopping consumer")
                    break
                except Exception as exc:
                    logger.error(
                        "Error processing message",
                        extra={
                            "error": {
                                "code": "DS_KAFKA_CONSUMER_ERROR",
                                "type": type(exc).__name__,
                                "message": str(exc),
                                "traceback": traceback.format_exc(),
                            },
                        },
                    )

        except Exception as exc:
            logger.error(
                "Failed to start consumer",
                extra={
                    "error": {
                        "code": "DS_KAFKA_CONSUMER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
        finally:
            self.stop()

    def _process_message(self, msg: Message) -> None:
        """
        Process a received message.

        Args:
            msg: Kafka message.

        Returns:
            None
        """
        try:
            raw_value = msg.value()
            if raw_value is None:
                raise DeserializationError(
                    message="Message value was None",
                    details={
                        "topic": msg.topic(),
                        "partition": msg.partition(),
                        "offset": msg.offset(),
                        "reason": "Message value was None",
                    },
                )

            data = json.loads(raw_value.decode("utf-8"))
            message = EventStream.deserialize(data)
            topic = msg.topic()

            logger.debug(
                "Received message",
                extra={
                    "topic": topic,
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                },
            )

            if topic in self.message_handlers:
                self.message_handlers[topic](message)
            else:
                logger.warning("No handler found for topic", extra={"topic": topic})
        except DeserializationError as exc:
            logger.error(
                "Failed to deserialize message",
                extra={
                    "error": {
                        "code": "DS_KAFKA_CONSUMER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
            raise exc
        except ConsumerError as exc:
            raise exc
        except Exception as exc:
            logger.error(
                "Error processing message",
                extra={
                    "error": {
                        "code": "DS_KAFKA_CONSUMER_ERROR",
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                },
            )
            raise ConsumerError(
                details={
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                },
            ) from exc

    def _on_assign(self, consumer: Any, partitions: Any) -> None:
        """
        Callback for when partitions are assigned to the consumer.

        Args:
            consumer: The Kafka consumer.
            partitions: The partitions assigned to the consumer.
        """
        member_id = consumer.memberid()
        logger.debug(
            "Partitions assigned",
            extra={"partitions": partitions, "member_id": member_id},
        )

    def _on_revoke(self, consumer: Any, partitions: Any) -> None:
        """
        Callback for when partitions are revoked from the consumer.

        Args:
            consumer: The Kafka consumer.
            partitions: The partitions revoked from the consumer.
        """
        member_id = consumer.memberid()
        logger.debug(
            "Partitions revoked",
            extra={"partitions": partitions, "member_id": member_id},
        )

    def stop(self) -> None:
        """
        Stop the consumer.

        Returns:
            None
        """
        self.running = False
        if self.consumer is None:
            return
        self.consumer.close()
        logger.debug("Consumer stopped")
