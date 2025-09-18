# Usage

## Kafka Configuration

Configure your Kafka connection using `KafkaConfig`:

```python
from dseventstream.kafka.kafka_config import KafkaConfig
config = KafkaConfig(
    bootstrap_servers="kafka-prod:9092",
    username="service-principal",
    password="secret"
)
```

## Producer/Consumer

Create producer and consumer services:

```python
from dseventstream.kafka.kafka_service import KafkaProducerService, KafkaConsumerService
producer = KafkaProducerService(config=config)
consumer = KafkaConsumerService(config=config, group_id="my-group")
```

## Sending Events

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

## Consuming Events

```python
def on_message(event_dict):
    print(event_dict)
consumer.consume("topic-name", on_message)
```
