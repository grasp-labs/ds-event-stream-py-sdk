"""
**File:** ``__init__.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Public exports for the Kafka consumer utilities.

Example
-------

.. code-block:: python

    from ds_event_stream_py_sdk.consumer import KafkaConsumer

    consumer = KafkaConsumer(topics=["events"])
"""

from .base import KafkaConsumer

__all__ = ["KafkaConsumer"]
