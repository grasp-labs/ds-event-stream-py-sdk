"""
**File:** ``01_event.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Minimal example for creating an ``EventStream`` and inspecting its serialized payload.

Example
-------

.. code-block:: python

    uv run python examples/01_event.py

You can also install the package in editable mode and run with ``python``:

.. code-block:: python

    uv run python -m examples.01_event
"""

from __future__ import annotations

import json
from uuid import uuid4

from ds_event_stream_py_sdk.models.v1 import EventStream
from ds_common_logger_py_lib import Logger

Logger()
logger = Logger.get_logger(__name__)


def main() -> None:
    """
    Create and print an EventStream payload.

    Returns:
        None.
    """

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        owner_id="owner_id",
        product_id=uuid4(),
        event_type="example.event",
        event_source="examples",
        created_by="examples/01_event.py",
        payload={"hello": "world"},
        context={"example": "context"},
    )
    logger.info(f"md5_hash={event.md5_hash}")

    serialized = event.serialize()
    logger.info(f"serialized={json.dumps(serialized, indent=2, sort_keys=True)}")

    deserialized = EventStream.deserialize(serialized)
    logger.info(f"deserialized={deserialized}")


if __name__ == "__main__":
    main()
