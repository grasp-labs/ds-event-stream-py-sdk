# ds-event-stream-py-sdk

A Python package from the DS Event Stream Python SDK.

## Installation

Install the package using pip:

```bash
pip install ds-event-stream-py-sdk
```

Or using uv (recommended):

```bash
uv pip install ds-event-stream-py-sdk
```

## Quick Start

```python
from ds_event_stream_py_sdk import __version__

print(f"ds-event-stream-py-sdk version: {__version__}")
```

## Features

- Kafka producer
- Kafka consumer
- Event stream model

## Usage

```python
import logging
from uuid import uuid4

from ds_common_logger_py_lib import Logger
from ds_event_stream_py_sdk.errors import ProducerError
from ds_event_stream_py_sdk.models.v1 import EventStream
from ds_event_stream_py_sdk.producer import KafkaProducer

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


producer = KafkaProducer(
    bootstrap_servers="b0.dev.kafka.ds.local:9095",
    sasl_username="ds.test.producer.v1",
    sasl_password="",
    timeout=5.0,
)

event = EventStream(
    session_id=uuid4(),
    tenant_id=uuid4(),
    event_type="example.event",
    event_source="examples",
    created_by="John Doe",
    payload={"hello": "world"},
)
producer.send_message(
    topic="ds.test.message.created.v1",
    message=event,
    key=str(event.session_id),
    timeout=5.0,
)
```

## Requirements

- Python 3.10 or higher
- ds-common-logger-py-lib
- ds-common-serde-py-lib
- confluent-kafka

## Documentation

Full documentation is available at:

- [GitHub Repository](https://github.com/grasp-labs/ds-event-stream-py-sdk)
- [Documentation Site](https://grasp-labs.github.io/ds-event-stream-py-sdk/)

## Development

To contribute or set up a development environment:

```bash
# Clone the repository
git clone https://github.com/grasp-labs/ds-event-stream-py-sdk.git
cd ds-event-stream-py-sdk

# Install development dependencies
uv sync --all-extras --dev

# Run tests
make test
```

See the [README](https://github.com/grasp-labs/ds-event-stream-py-sdk#readme)
for more information.

## License

This package is licensed under the Apache License 2.0.
See the [LICENSE-APACHE](https://github.com/grasp-labs/ds-event-stream-py-sdk/blob/main/LICENSE-APACHE)
file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/grasp-labs/ds-event-stream-py-sdk/issues)
- **Releases**: [GitHub Releases](https://github.com/grasp-labs/ds-event-stream-py-sdk/releases)
