"""
A Python package from the ds-common library collection.

**File:** ``__init__.py``
**Region:** ``ds-event-stream-py-sdk``

Example:

.. code-block:: python

    from ds_event_stream_py_sdk import __version__

    print(f"Package version: {__version__}")
"""

from pathlib import Path

from .consumer import KafkaConsumer
from .models.v1 import EventStream
from .producer import KafkaProducer

_VERSION_FILE = Path(__file__).parent.parent.parent / "VERSION.txt"
__version__ = _VERSION_FILE.read_text().strip() if _VERSION_FILE.exists() else "0.0.0"

__all__ = ["EventStream", "KafkaConsumer", "KafkaProducer", "__version__"]
