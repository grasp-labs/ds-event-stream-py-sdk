
# ds-event-stream-python-sdk

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/grasp-labs/ds-event-stream-python-sdk.git
    cd ds-event-stream-python-sdk
    ```

2. **Set up a Python virtual environment:**
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    # Or use 'uv pip install -r requirements.txt' if using uv
    ```

4. **(Optional) Generate models from schemas:**
    ```sh
    make generate-models
    ```

A Python SDK for producing and consuming events on a Kafka-based event stream, following Grasp Labs' event stream conventions.

## Features
- **Dataclass Models**: Auto-generated from JSON schemas for type-safe event handling.
- **Kafka Producer/Consumer Services**: Simple interfaces for sending and receiving events.
- **Service Principal Configuration**: Centralized config via `KafkaConfig` for authentication and connection settings.
- **Mockable for Testing**: All Kafka interactions can be mocked for CI and local testing.

## Package Structure
```
dseventstream/
    models/
        event.py           # Event dataclass (auto-generated)
        system_topics.py   # System topics enum (auto-generated)
    kafka/
        kafka_service.py   # Producer/Consumer service classes
        kafka_config.py    # Shared config for Kafka principals
```

## Usage

### 1. Configure Kafka Connection
```python
from dseventstream.kafka.kafka_config import KafkaConfig
config = KafkaConfig(
    bootstrap_servers="kafka-prod:9092",
    username="service-principal",
    password="secret"
)
```

### 2. Create Producer/Consumer
```python
from dseventstream.kafka.kafka_service import KafkaProducerService, KafkaConsumerService
producer = KafkaProducerService(config=config)
consumer = KafkaConsumerService(config=config, group_id="my-group")
```

### 3. Send an Event
```python
from dseventstream.models.event import Event
event = Event(
    id="event-id",
    session_id="session-id",
    request_id="request-id",
    tenant_id="tenant-id",
    event_type="type",
    event_source="source",
    metadata={"key": "value"},
    timestamp="2025-09-18T00:00:00Z",
    created_by="user",
    md5_hash="..."
)
producer.send("topic-name", event)
```

### 4. Consume Events
```python
def on_message(event_dict):
    print(event_dict)
consumer.consume("topic-name", on_message)
```

## Testing
- All Kafka interactions are mockable using `unittest.mock`.
- Example tests are provided in the `tests/` folder.

## Security
- SASL_PLAINTEXT and SCRAM-SHA-512 are used for authentication (see `KafkaConfig`).

## Auto-Generated Models
- Models are generated from JSON schemas in the `schemas/` folder using the Makefile.

## License
MIT
