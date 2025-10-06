# ds-event-stream-python-sdk

A Python SDK for producing and consuming events on a Kafka-based event stream, following Grasp Labs' event stream conventions.

## Features

- **Dataclass Models**: Auto-generated from JSON schemas for type-safe event handling
- **Kafka Producer/Consumer Services**: Simple interfaces for sending and receiving events
- **Service Principal Configuration**: Centralized config via `KafkaConfig` for authentication and connection settings
- **Mockable for Testing**: All Kafka interactions can be mocked for CI and local testing

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/grasp-labs/ds-event-stream-python-sdk.git
   cd ds-event-stream-python-sdk
   ```

2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

4. **(Optional) Generate models from schemas:**
   ```bash
   make generate-models
   ```

## Quick Start

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
    print(f"Received event: {event_dict}")

consumer.consume("topic-name", on_message)
```

## Package Structure

```
dseventstream/
├── models/
│   ├── event.py           # Event dataclass (auto-generated)
│   └── system_topics.py   # System topics enum (auto-generated)
└── kafka/
    ├── kafka_service.py   # Producer/Consumer service classes
    └── kafka_config.py    # Shared config for Kafka principals

docs/                      # Documentation source files
├── README.md             # Main documentation
├── usage.md              # Usage examples
├── api.md                # API reference
├── testing.md            # Testing guide
└── license.md            # License information

tests/                    # Test suite
├── test_kafka_producer.py
├── test_kafka_consumer.py
└── test_kafka_mock.py

schemas/                  # JSON schemas for model generation
├── event.json
└── system-topics.json

.github/workflows/        # CI/CD pipelines
├── deploy-docs.yml       # Documentation deployment
└── deploy-pypi.yml       # PyPI release automation
```

## API Reference

### Core Classes

#### `KafkaConfig`
Centralized configuration for Kafka connections.

```python
from dseventstream.kafka.kafka_config import KafkaConfig

# Production configuration
config = KafkaConfig(
    bootstrap_servers="kafka-prod:9092",
    username="service-principal",
    password="secret"
)

# Development configuration
config = KafkaConfig(bootstrap_servers="localhost:9092")
```

#### `KafkaProducerService`
Service for publishing events to Kafka topics.

```python
from dseventstream.kafka.kafka_service import KafkaProducerService

producer = KafkaProducerService(config=config)
producer.send("topic-name", event, key="optional-key")
```

#### `KafkaConsumerService`
Service for consuming events from Kafka topics.

```python
from dseventstream.kafka.kafka_service import KafkaConsumerService

consumer = KafkaConsumerService(config=config, group_id="my-group")

def handle_message(event_dict):
    print(f"Received: {event_dict}")

consumer.consume("topic-name", handle_message)
```

#### `Event`
Auto-generated dataclass for event structure.

```python
from dseventstream.models.event import Event

event = Event(
    id="unique-event-id",
    session_id="session-123",
    request_id="request-456",
    tenant_id="tenant-789",
    event_type="user.action",
    event_source="web-app",
    metadata={"key": "value"},
    timestamp="2025-01-01T00:00:00Z",
    created_by="user-id",
    md5_hash="computed-hash"
)
```

## Development

### Prerequisites

- Python 3.13+
- Make (for code generation)

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Generate models from schemas
make generate-models

# Run tests
make test
```

### Testing

All Kafka interactions are mockable using `unittest.mock`. Example tests are provided in the `tests/` folder.

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test
python -m unittest tests.test_kafka_producer
```

## Security

- SASL_PLAINTEXT and SCRAM-SHA-512 are used for authentication (see `KafkaConfig`)
- For security issues, please see our [Security Policy](https://github.com/grasp-labs/.github/blob/main/SECURITY.md)

## Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ds-event-stream-py-sdk.git
   cd ds-event-stream-py-sdk
   ```

2. **Set up Development Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Make Changes and Test**
   ```bash
   # Generate models if needed
   make generate-models

   # Run tests
   make test
   # or
   python -m unittest discover -s tests
   ```

4. **Create Pull Request**
   - Create a feature branch: `git checkout -b feature/your-feature-name`
   - Make your changes and commit them
   - Push to your fork and create a PR

### Automated Release Process

This project uses **automated releases** when PRs are merged to `main`. The version bump type is determined by your PR title:

#### Version Bump Types

| PR Title Contains | Version Bump | Example |
|-------------------|--------------|---------|
| `major`, `breaking`, `BREAKING CHANGE` | **Major** | `0.1.0` → `1.0.0` |
| `feat`, `feature`, `minor` | **Minor** | `0.1.0` → `0.2.0` |
| Default (bug fixes, docs, etc.) | **Patch** | `0.1.0` → `0.1.1` |

#### Examples

```bash
# Patch release (bug fix)
PR Title: "Fix kafka connection timeout issue"
→ Version: 0.1.0 → 0.1.1

# Minor release (new feature)
PR Title: "feat: Add event filtering capabilities"
→ Version: 0.1.0 → 0.2.0

# Major release (breaking change)
PR Title: "BREAKING CHANGE: Redesign API interface"
→ Version: 0.1.0 → 1.0.0
```

#### What Happens When PR is Merged

1. ✅ **Version automatically bumped** in `pyproject.toml`
2. ✅ **Git tag created** (`v{new_version}`)
3. ✅ **GitHub release created** with changelog
4. ✅ **Package published to PyPI** automatically

### Code Style and Standards

- Follow PEP 8 for Python code style
- Add type hints where appropriate
- Write tests for new functionality
- Update documentation for API changes
- Use descriptive commit messages

### Testing

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_kafka_producer

# Run with coverage (if installed)
coverage run -m unittest discover -s tests
coverage report
```

## Documentation

Full documentation is available at: https://grasp-labs.github.io/ds-event-stream-python-sdk/

## Installation for End Users

### From PyPI (Recommended)

```bash
pip install ds-event-stream-python-sdk
```

### From Source

```bash
git clone https://github.com/grasp-labs/ds-event-stream-py-sdk.git
cd ds-event-stream-py-sdk
pip install -e .
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.