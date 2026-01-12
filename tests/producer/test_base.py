"""
**File:** ``test_base.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Smoke tests for the producer module (imports and basic API surface).
"""

from __future__ import annotations

import importlib
from typing import Any, cast
from uuid import uuid4

import pytest
from ds_common_serde_py_lib.errors import SerializationError

import ds_event_stream_py_sdk.producer.base as producer_base
from ds_event_stream_py_sdk.errors import ProducerError
from ds_event_stream_py_sdk.models.v1 import EventStream


def test_producer_base_module_imports() -> None:
    """
    Verify the producer base module can be imported.

    Returns:
        None.
    """

    module = importlib.import_module("ds_event_stream_py_sdk.producer.base")
    assert hasattr(module, "KafkaProducer")


def test_producer_package_exposes_kafka_producer() -> None:
    """
    Verify ``KafkaProducer`` is exported from the producer package.

    Returns:
        None.
    """

    module = importlib.import_module("ds_event_stream_py_sdk.producer")
    assert hasattr(module, "KafkaProducer")


class _FakeMessage:
    def __init__(self, *, topic: str = "events", partition: int = 0, offset: int = 1) -> None:
        self._topic = topic
        self._partition = partition
        self._offset = offset

    def topic(self) -> str:
        return self._topic

    def partition(self) -> int:
        return self._partition

    def offset(self) -> int:
        return self._offset


class _FakeProducerClient:
    def __init__(self, config: dict[str, Any], *, raise_on_produce: bool = False) -> None:
        self.config = config
        self.raise_on_produce = raise_on_produce
        self.produced: list[dict[str, Any]] = []
        self.flushed: list[float] = []
        self.flush_remaining: int = 0

    def produce(self, **kwargs: Any) -> None:
        if self.raise_on_produce:
            raise RuntimeError("produce failed")
        self.produced.append(kwargs)
        callback = kwargs.get("callback")
        if callback is not None:
            callback(None, _FakeMessage(topic=kwargs.get("topic", "events")))

    def flush(self, timeout: float) -> int:
        self.flushed.append(timeout)
        return self.flush_remaining


def test_producer_init_sets_plaintext_security_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify default auth mode is PLAINTEXT when SASL is not provided.

    Returns:
        None.
    """

    created: dict[str, Any] = {}

    def _factory(config: dict[str, Any]) -> _FakeProducerClient:
        created["client"] = _FakeProducerClient(config)
        return created["client"]

    monkeypatch.setattr(producer_base, "Producer", _factory)

    producer = producer_base.KafkaProducer()
    assert producer.config["security.protocol"] == "PLAINTEXT"
    assert created["client"].config["security.protocol"] == "PLAINTEXT"


def test_producer_init_sets_sasl_plaintext_when_credentials_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify SASL settings are applied when credentials are provided.

    Returns:
        None.
    """

    created: dict[str, Any] = {}

    def _factory(config: dict[str, Any]) -> _FakeProducerClient:
        created["client"] = _FakeProducerClient(config)
        return created["client"]

    monkeypatch.setattr(producer_base, "Producer", _factory)

    producer = producer_base.KafkaProducer(sasl_username="u", sasl_password="p")
    assert producer.config["security.protocol"] == "SASL_PLAINTEXT"
    assert producer.config["sasl.username"] == "u"
    assert producer.config["sasl.password"] == "p"


def test_send_message_produces_and_flushes(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify sending a message calls produce and flushes the producer.

    Returns:
        None.
    """

    client = _FakeProducerClient({})
    client.flush_remaining = 0
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()
    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
        payload={"k": "v"},
    )

    producer.send_message(topic="events", message=event, key="k1")

    assert len(client.produced) == 1
    produced = client.produced[0]
    assert produced["topic"] == "events"
    assert isinstance(produced["value"], (bytes, bytearray))
    assert produced["key"] == b"k1"
    assert client.flushed and client.flushed[-1] == 60.0


def test_send_message_wraps_unknown_errors_in_producer_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify non-serialization failures raise ``ProducerError``.

    Returns:
        None.
    """

    client = _FakeProducerClient({}, raise_on_produce=True)
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()
    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )

    with pytest.raises(ProducerError):
        producer.send_message(topic="events", message=event)


def test_send_message_raises_producer_error_when_flush_times_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify non-zero flush return value raises ``ProducerError``.

    Returns:
        None.
    """

    client = _FakeProducerClient({})
    client.flush_remaining = 1
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()
    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )

    with pytest.raises(ProducerError) as exc_info:
        producer.send_message(topic="events", message=event, key="k1", timeout=5.0)

    assert exc_info.value.details["topic"] == "events"
    assert exc_info.value.details["key"] == "k1"
    assert exc_info.value.details["timeout"] == 5.0
    assert exc_info.value.details["undelivered_messages"] == 1


def test_send_message_reraises_serialization_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify ``SerializationError`` is not wrapped.

    Returns:
        None.
    """

    client = _FakeProducerClient({})
    client.flush_remaining = 0
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )

    def _raise_serialization_error(_: Any) -> str:
        raise SerializationError(message="boom", details={})

    monkeypatch.setattr(producer_base.json, "dumps", _raise_serialization_error)

    with pytest.raises(SerializationError):
        producer.send_message(topic="events", message=event)


def test_callback_paths_do_not_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify delivery callback handles success and failure cases.

    Returns:
        None.
    """

    client = _FakeProducerClient({})
    client.flush_remaining = 0
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()
    producer._callback(cast("Any", RuntimeError("x")), cast("Any", _FakeMessage(topic="events")))
    producer._callback(None, cast("Any", _FakeMessage(topic="events")))


def test_close_flushes(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify close flushes the producer.

    Returns:
        None.
    """

    client = _FakeProducerClient({})
    client.flush_remaining = 0
    monkeypatch.setattr(producer_base, "Producer", lambda _config: client)

    producer = producer_base.KafkaProducer()
    producer.close()

    assert client.flushed and client.flushed[-1] == 60.0
