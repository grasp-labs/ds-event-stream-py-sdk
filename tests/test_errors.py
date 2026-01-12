"""
**File:** ``test_errors.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Sanity tests for the SDK's error types.
"""

from __future__ import annotations

from ds_event_stream_py_sdk.errors import ConsumerError, KafkaException, ProducerError


def test_kafka_exception_defaults_are_set() -> None:
    """
    Verify default fields are populated and consistent.

    Returns:
        None.
    """

    exc = KafkaException()

    assert isinstance(exc, Exception)
    assert exc.message != ""
    assert exc.code != ""
    assert exc.status_code == 500
    assert isinstance(exc.details, dict)


def test_consumer_and_producer_errors_inherit_kafka_exception() -> None:
    """
    Verify typed errors inherit from the base Kafka exception.

    Returns:
        None.
    """

    assert issubclass(ConsumerError, KafkaException)
    assert issubclass(ProducerError, KafkaException)


def test_details_defaults_to_empty_dict() -> None:
    """
    Verify details defaults to an empty dict when omitted.

    Returns:
        None.
    """

    exc = ConsumerError(details=None)
    assert isinstance(exc.details, dict)
    assert exc.details == {}


def test_producer_error_defaults_are_set() -> None:
    """
    Verify producer error sets expected defaults.

    Returns:
        None.
    """

    exc = ProducerError()
    assert isinstance(exc, KafkaException)
    assert exc.code == "DS_KAFKA_PRODUCER_ERROR"
    assert exc.status_code == 500
