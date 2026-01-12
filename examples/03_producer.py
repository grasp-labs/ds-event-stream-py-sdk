"""
**File:** ``03_producer.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Minimal example showing how to configure a ``KafkaProducer``.

This script does not send messages by default to keep it safe to run without a
Kafka broker. To publish to a real broker, pass ``--send``.

Example
-------

.. code-block:: python

    uv run python examples/03_producer.py

To send to a real broker:

.. code-block:: python

    uv run python examples/03_producer.py --send --bootstrap-servers localhost:9092 --topic events
"""

from __future__ import annotations

import logging
from uuid import uuid4

from ds_common_logger_py_lib import Logger
from ds_event_stream_py_sdk.errors import ProducerError
from ds_event_stream_py_sdk.models.v1 import EventStream
from ds_event_stream_py_sdk.producer import KafkaProducer

Logger(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def main() -> None:
    """
    Configure a producer and (optionally) send an event.

    Returns:
        None.
    """
    producer = KafkaProducer(bootstrap_servers="localhost:9092")

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="example.event",
        event_source="examples",
        created_by="examples/03_producer.py",
        payload={"hello": "world"},
    )

    logger.info("Producer configured.")
    logger.info("Sending message (this will block if broker is unreachable).")

    try:
        producer.send_message(
            topic="events",
            message=event,
            key=str(event.session_id),
            timeout=5.0,
        )
    except ProducerError as exc:
        logger.error(exc.__dict__)


if __name__ == "__main__":
    main()
