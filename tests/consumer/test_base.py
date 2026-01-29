"""
**File:** ``test_base.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Smoke tests for the consumer module (imports and basic API surface).
"""

from __future__ import annotations

import importlib
import json
from typing import Any
from uuid import uuid4

import pytest
from ds_common_serde_py_lib.errors import DeserializationError

import ds_event_stream_py_sdk.consumer.base as consumer_base
from ds_event_stream_py_sdk.consumer.base import KafkaConsumer
from ds_event_stream_py_sdk.errors import ConsumerError
from ds_event_stream_py_sdk.models.v1 import EventStream

BOOTSTRAP_SERVERS = "localhost:9092"


def test_consumer_base_module_imports() -> None:
    """
    Verify the consumer base module can be imported.

    Returns:
        None.
    """

    module = importlib.import_module("ds_event_stream_py_sdk.consumer.base")
    assert hasattr(module, "KafkaConsumer")


def test_consumer_package_exposes_kafka_consumer() -> None:
    """
    Verify ``KafkaConsumer`` is exported from the consumer package.

    Returns:
        None.
    """

    module = importlib.import_module("ds_event_stream_py_sdk.consumer")
    assert hasattr(module, "KafkaConsumer")


class _FakeMessage:
    def __init__(
        self,
        *,
        topic: str = "events",
        partition: int = 0,
        offset: int = 1,
        value: bytes | None = None,
        error: Any | None = None,
    ) -> None:
        self._topic = topic
        self._partition = partition
        self._offset = offset
        self._value = value
        self._error = error

    def topic(self) -> str:
        return self._topic

    def partition(self) -> int:
        return self._partition

    def offset(self) -> int:
        return self._offset

    def value(self) -> bytes | None:
        return self._value

    def error(self) -> Any | None:
        return self._error


class _FakeConsumerClient:
    def __init__(self, *, commit_raises: bool = False) -> None:
        self._commit_raises = commit_raises
        self.closed = False
        self.committed: list[Any] = []

    def commit(self, msg: Any) -> None:
        if self._commit_raises:
            raise RuntimeError("commit failed")
        self.committed.append(msg)

    def close(self) -> None:
        self.closed = True


def test_add_message_handler_registers_for_str_and_invokes_handler() -> None:
    """
    Verify string topic registration and wrapper invocation.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    called: dict[str, Any] = {"count": 0, "arg": None}

    def handler(message: EventStream, arg: str) -> None:
        called["count"] += 1
        called["arg"] = arg
        assert isinstance(message, EventStream)

    consumer.add_message_handler("events", handler, "ok")

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )
    consumer.message_handlers["events"](event)

    assert called["count"] == 1
    assert called["arg"] == "ok"


def test_add_message_handler_registers_for_list_of_topics() -> None:
    """
    Verify list topic registration.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["a", "b"])

    def handler(_: EventStream) -> None:
        return None

    consumer.add_message_handler(["a", "b"], handler)
    assert "a" in consumer.message_handlers
    assert "b" in consumer.message_handlers


def test_commit_message_noops_without_current_message_or_client() -> None:
    """
    Verify commit is a no-op when not ready.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    consumer.commit_message()


def test_commit_message_raises_consumer_error_on_commit_failure() -> None:
    """
    Verify commit failures are wrapped in ``ConsumerError``.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    consumer.consumer = _FakeConsumerClient(commit_raises=True)  # type: ignore[assignment]
    consumer.current_message = _FakeMessage(topic="events", partition=1, offset=2)  # type: ignore[assignment]

    with pytest.raises(ConsumerError) as exc_info:
        consumer.commit_message()

    assert exc_info.value.details["topic"] == "events"
    assert exc_info.value.details["partition"] == 1
    assert exc_info.value.details["offset"] == 2


def test_process_message_calls_handler_for_topic() -> None:
    """
    Verify message bytes are deserialized and passed to the topic handler.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    called: dict[str, int] = {"count": 0}

    def handler(_: EventStream) -> None:
        called["count"] += 1

    consumer.add_message_handler("events", handler)

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
        payload={"k": "v"},
    )
    msg = _FakeMessage(
        topic="events",
        value=json.dumps(event.serialize()).encode("utf-8"),
    )

    consumer._process_message(msg)
    assert called["count"] == 1


def test_process_message_raises_deserialization_error_on_none_value() -> None:
    """
    Verify missing message value raises ``DeserializationError``.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    msg = _FakeMessage(topic="events", value=None)

    with pytest.raises(DeserializationError):
        consumer._process_message(msg)


def test_process_message_raises_consumer_error_on_invalid_json() -> None:
    """
    Verify invalid JSON payloads raise ``ConsumerError``.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    msg = _FakeMessage(topic="events", partition=3, offset=4, value=b"{")

    with pytest.raises(ConsumerError) as exc_info:
        consumer._process_message(msg)

    assert exc_info.value.details["topic"] == "events"
    assert exc_info.value.details["partition"] == 3
    assert exc_info.value.details["offset"] == 4


def test_stop_closes_consumer_client() -> None:
    """
    Verify stop closes the underlying consumer client.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    client = _FakeConsumerClient()
    consumer.consumer = client  # type: ignore[assignment]

    consumer.stop()
    assert client.closed is True


def test_on_assign_and_on_revoke_do_not_raise() -> None:
    """
    Verify assign/revoke callbacks do not raise.

    Returns:
        None.
    """

    class _FakeKafkaConsumer:
        def memberid(self) -> str:
            return "member-1"

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    consumer._on_assign(_FakeKafkaConsumer(), partitions=[1])
    consumer._on_revoke(_FakeKafkaConsumer(), partitions=[1])


def test_start_subscribes_polls_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify start creates consumer, subscribes, and closes on interrupt.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])

    class _FakeKafkaClient:
        def __init__(self, _config: dict[str, Any]) -> None:
            self.subscribed_topics: list[str] = []
            self.closed = False

        def subscribe(self, topics: list[str], on_assign: Any, on_revoke: Any) -> None:
            self.subscribed_topics = topics
            on_assign(self, partitions=[0])
            on_revoke(self, partitions=[0])

        def poll(self, timeout: float) -> Any:
            del timeout
            raise KeyboardInterrupt

        def close(self) -> None:
            self.closed = True

        def memberid(self) -> str:
            return "member-1"

    monkeypatch.setattr(consumer_base, "Consumer", _FakeKafkaClient)

    consumer.start()
    assert consumer.consumer is not None
    assert getattr(consumer.consumer, "closed", False) is True


def test_consumer_init_sets_sasl_plaintext_when_credentials_provided() -> None:
    """
    Verify SASL settings are applied when credentials are provided.

    Returns:
        None.
    """

    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        topics=["events"],
        sasl_username="u",
        sasl_password="p",
    )

    assert consumer.config["security.protocol"] == "SASL_PLAINTEXT"
    assert consumer.config["sasl.username"] == "u"
    assert consumer.config["sasl.password"] == "p"


def test_commit_message_success_calls_commit() -> None:
    """
    Verify commit_message calls into the underlying consumer client.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    client = _FakeConsumerClient()
    consumer.consumer = client  # type: ignore[assignment]
    consumer.current_message = _FakeMessage(topic="events", partition=1, offset=2)  # type: ignore[assignment]

    consumer.commit_message()
    assert len(client.committed) == 1


def test_process_message_without_handler_does_not_raise() -> None:
    """
    Verify messages without a registered handler are tolerated.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )
    msg = _FakeMessage(
        topic="events",
        value=json.dumps(event.serialize()).encode("utf-8"),
    )

    consumer._process_message(msg)


def test_process_message_reraises_consumer_error_from_handler() -> None:
    """
    Verify ``ConsumerError`` raised by handlers is re-raised.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])

    def handler(_: EventStream) -> None:
        raise ConsumerError(details={"reason": "handler failed"})

    consumer.add_message_handler("events", handler)

    event = EventStream(
        session_id=uuid4(),
        tenant_id=uuid4(),
        event_type="test.event",
        event_source="unit-test",
        created_by="pytest",
    )
    msg = _FakeMessage(
        topic="events",
        value=json.dumps(event.serialize()).encode("utf-8"),
    )

    with pytest.raises(ConsumerError):
        consumer._process_message(msg)


def test_stop_noops_without_client() -> None:
    """
    Verify stop is safe when no client exists.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])
    consumer.stop()


def test_start_exits_after_polling_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify start can exit cleanly when poll returns None.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])

    class _FakeKafkaClient:
        def __init__(self, _config: dict[str, Any]) -> None:
            self.closed = False

        def subscribe(self, _topics: list[str], on_assign: Any, on_revoke: Any) -> None:
            on_assign(self, partitions=[0])
            on_revoke(self, partitions=[0])

        def poll(self, timeout: float) -> Any:
            del timeout
            consumer.running = False
            return None

        def close(self) -> None:
            self.closed = True

        def memberid(self) -> str:
            return "member-1"

    monkeypatch.setattr(consumer_base, "Consumer", _FakeKafkaClient)

    consumer.start()
    assert consumer.consumer is not None
    assert getattr(consumer.consumer, "closed", False) is True


def test_start_handles_message_error_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify start handles messages with errors.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])

    class _FakeKafkaError:
        def __init__(self, code: int) -> None:
            self._code = code

        def code(self) -> int:
            return self._code

    class _FakeKafkaErrorType:
        _PARTITION_EOF = 1

    class _FakeKafkaClient:
        def __init__(self, _config: dict[str, Any]) -> None:
            self.closed = False

        def subscribe(self, _topics: list[str], on_assign: Any, on_revoke: Any) -> None:
            on_assign(self, partitions=[0])
            on_revoke(self, partitions=[0])

        def poll(self, timeout: float) -> Any:
            del timeout
            consumer.running = False
            return _FakeMessage(error=_FakeKafkaError(2))

        def close(self) -> None:
            self.closed = True

        def memberid(self) -> str:
            return "member-1"

    monkeypatch.setattr(consumer_base, "Consumer", _FakeKafkaClient)
    monkeypatch.setattr(consumer_base, "KafkaError", _FakeKafkaErrorType)

    consumer.start()
    assert consumer.consumer is not None
    assert getattr(consumer.consumer, "closed", False) is True


def test_start_catches_exception_in_process_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify start catches unexpected exceptions from message processing.

    Returns:
        None.
    """

    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, topics=["events"])

    class _FakeKafkaClient:
        def __init__(self, _config: dict[str, Any]) -> None:
            self.closed = False

        def subscribe(self, _topics: list[str], on_assign: Any, on_revoke: Any) -> None:
            on_assign(self, partitions=[0])
            on_revoke(self, partitions=[0])

        def poll(self, timeout: float) -> Any:
            del timeout
            return _FakeMessage(value=b"{}")

        def close(self) -> None:
            self.closed = True

        def memberid(self) -> str:
            return "member-1"

    def _boom(_: Any) -> None:
        consumer.running = False
        raise ValueError("boom")

    monkeypatch.setattr(consumer_base, "Consumer", _FakeKafkaClient)
    monkeypatch.setattr(consumer, "_process_message", _boom)

    consumer.start()
    assert consumer.consumer is not None
    assert getattr(consumer.consumer, "closed", False) is True
