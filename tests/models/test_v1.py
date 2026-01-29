"""
**File:** ``test_v1.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Basic construction tests for the v1 event models.
"""

from __future__ import annotations

from uuid import uuid4

from ds_event_stream_py_sdk.models.v1 import EventStream


def test_event_stream_constructs_and_sets_md5_hash() -> None:
    """
    Verify the model can be constructed and computes an md5 hash by default.

    Returns:
        None.
    """

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
        payload={"hello": "world"},
    )

    assert event.md5_hash is not None
    assert isinstance(event.md5_hash, str)
    assert len(event.md5_hash) == 32
    assert event.timestamp.tzinfo is not None
