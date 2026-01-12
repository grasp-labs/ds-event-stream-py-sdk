"""
**File:** ``__init__.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Public exports for the Kafka producer utilities.

Example
-------

.. code-block:: python

    from ds_event_stream_py_sdk.producer import KafkaProducer

    producer = KafkaProducer()
"""

from .base import KafkaProducer

__all__ = ["KafkaProducer"]
