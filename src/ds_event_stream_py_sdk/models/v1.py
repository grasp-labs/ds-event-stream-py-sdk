"""
Event models for version 1 of the data pipeline events.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from ds_common_serde_py_lib import Serializable


@dataclass(kw_only=True)
class EventStream(Serializable):
    """Base event stream model for pipeline events."""

    id: UUID = field(default_factory=lambda: uuid4())
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
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    md5_hash: str | None = None

    def __post_init__(self) -> None:
        """
        Post-initialize the event stream.
        """
        if self.md5_hash is None:
            self.md5_hash = hashlib.md5(json.dumps(self.serialize()).encode("utf-8")).hexdigest()
