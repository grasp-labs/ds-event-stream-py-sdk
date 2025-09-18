# API Reference

## dseventstream.kafka.kafka_config.KafkaConfig
- Centralized configuration for Kafka service principals.
- Hardcoded: `security_protocol=SASL_PLAINTEXT`, `sasl_mechanism=SCRAM-SHA-512`
- Parameters:
  - `bootstrap_servers`: Kafka broker address
  - `username`: SASL username
  - `password`: SASL password
  - `extra`: Optional dict for additional config
- Method: `to_dict()` returns config for Kafka clients

## dseventstream.kafka.kafka_service.KafkaProducerService
- Constructor: `KafkaProducerService(config: KafkaConfig)`
- Method: `send(topic: str, event: Event, key: Optional[str] = None)`

## dseventstream.kafka.kafka_service.KafkaConsumerService
- Constructor: `KafkaConsumerService(config: KafkaConfig, group_id: str)`
- Method: `consume(topic: str, on_message: Callable[[Any], None])`

## dseventstream.models.event.Event
- Auto-generated dataclass for event payloads

## dseventstream.models.system_topics.EventID
- Auto-generated enum for system topics
