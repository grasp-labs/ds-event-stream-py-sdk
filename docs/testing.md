# Testing

## Mocking Kafka
All Kafka producer and consumer interactions can be mocked using `unittest.mock`.

Example:
```python
from unittest.mock import patch, MagicMock
from dseventstream.kafka.kafka_service import KafkaProducerService
from dseventstream.kafka.kafka_config import KafkaConfig

@patch("dseventstream.kafka.kafka_service.Producer")
def test_send_event(mock_producer_class):
    mock_producer = MagicMock()
    mock_producer_class.return_value = mock_producer
    config = KafkaConfig(bootstrap_servers="localhost:9092")
    producer = KafkaProducerService(config=config)
    # ...
```

## Running Tests
Run all tests:
```sh
python -m unittest discover -s tests
```

## CI/CD
- Tests do not require a running Kafka broker.
- See `tests/` for examples.
