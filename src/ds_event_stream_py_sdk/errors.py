"""
**File:** ``errors.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Custom exception types for the DS event stream SDK.

Example
-------

.. code-block:: python

    from ds_event_stream_py_sdk.errors import ConsumerError

    raise ConsumerError("Failed to process message")
"""

from typing import Any


class KafkaException(Exception):
    """Exception raised when a DS event stream encounters an error."""

    def __init__(
        self,
        message: str = "DS event stream operation failed",
        code: str = "DS_KAFKA_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a Kafka exception.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            status_code: HTTP-ish status code associated with the error.
            details: Optional extra details to help diagnose the error.

        Example:
            >>> exc = KafkaException()
            >>> exc.status_code
            500
        """
        self.code = code
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConsumerError(KafkaException):
    """Exception raised when a DS event stream consumer encounters an error."""

    def __init__(
        self,
        message: str = "DS event stream consumer operation failed",
        code: str = "DS_KAFKA_CONSUMER_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a consumer error.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            status_code: HTTP-ish status code associated with the error.
            details: Optional extra details to help diagnose the error.

        Example:
            >>> exc = ConsumerError()
            >>> exc.status_code
            500
        """
        super().__init__(message, code, status_code, details)


class ProducerError(KafkaException):
    """Exception raised when a DS event stream producer encounters an error."""

    def __init__(
        self,
        message: str = "DS event stream producer operation failed",
        code: str = "DS_KAFKA_PRODUCER_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a producer error.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            status_code: HTTP-ish status code associated with the error.
            details: Optional extra details to help diagnose the error.

        Example:
            >>> exc = ProducerError()
            >>> exc.status_code
            500
        """
        super().__init__(message, code, status_code, details)
