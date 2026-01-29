"""
**File:** ``__init__.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
A Python SDK for working with DS event streams, providing Kafka producers, consumers, and related models.

Example
-------
.. code-block:: python

    from ds_event_stream_py_sdk import __version__

    print(f"Package version: {__version__}")
"""

from importlib.metadata import version

from .consumer import KafkaConsumer
from .models.v1 import EventStream
from .producer import KafkaProducer

__version__ = version("ds-event-stream-py-sdk")
__all__ = ["EventStream", "KafkaConsumer", "KafkaProducer", "__version__"]
