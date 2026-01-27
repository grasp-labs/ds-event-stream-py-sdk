"""
**File:** ``02_consumer.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Minimal example showing how to configure a ``KafkaConsumer`` and register a handler.

This script does not start consuming by default to keep it safe to run without a
Kafka broker. To use it against a real broker, follow the comments in ``main``.

Example
-------

.. code-block:: python

    uv run python examples/02_consumer.py

"""

from __future__ import annotations
import logging

from ds_event_stream_py_sdk.consumer import KafkaConsumer
from ds_event_stream_py_sdk.models.v1 import EventStream
from ds_common_logger_py_lib import Logger

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def handle_event(event: EventStream, consumer: KafkaConsumer) -> None:
    """
    Handle a received event.

    Args:
        event: The decoded event.

    Returns:
        None.
    """

    logger.info(f"received event_type={event.event_type} id={event.id}")
    consumer.commit_message()


def main() -> None:
    """
    Configure a consumer and register a message handler.

    Returns:
        None.
    """

    consumer = KafkaConsumer(
        bootstrap_servers="b0.dev.kafka.ds.local:9095",
        sasl_username="ds.test.consumer.v1",
        sasl_password="",
        topics=["ds.test.message.created.v1"],
        enable_auto_commit=False,
    )

    consumer.add_message_handler("ds.test.message.created.v1", handle_event, consumer)
    consumer.start()


if __name__ == "__main__":
    main()
