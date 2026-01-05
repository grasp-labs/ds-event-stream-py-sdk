"""
Event models for version 1 of the data pipeline events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

# TODO: Import ds-common-serde-py-lib and use it to serialize and deserialize the event stream.
from ds_common_serde_py_lib import Serializable


@dataclass(kw_only=True)
class EventStream(Serializable):
    """Base event stream model for pipeline events."""

    id: UUID
    session_id: UUID
    request_id: UUID | None = None
    tenant_id: UUID
    owner_id: str | None = None
    product_id: UUID | None = None
    event_type: str
    event_source: str
    event_source_uri: str | None = None
    affected_entity_uri: str | None = None
    message: str | None = None
    payload: dict[str, Any] | None = None
    payload_uri: str | None = None
    context: dict[str, Any] | None = None
    context_uri: str | None = None
    metadata: dict[str, Any] | None = None
    tags: dict[str, Any] | None = None
    timestamp: datetime
    created_by: str
    md5_hash: str
