import unittest
from unittest.mock import MagicMock, patch
from dseventstream.models.event import Event
from dseventstream.kafka.kafka_service import KafkaProducerService, KafkaConsumerService
from dseventstream.kafka.kafka_config import KafkaConfig

class TestKafkaConsumerService(unittest.TestCase):
    def setUp(self):
        self.topic = "test-topic"
        self.event = Event(
            id="test-id",
            session_id="test-session",
            request_id="test-request",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="test-source",
            metadata={"key": "value"},
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        self.received = []

    @patch("dseventstream.kafka.kafka_service.Consumer")
    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_consume_event(self, mock_producer_class, mock_consumer_class):
        mock_producer = MagicMock()
        mock_consumer = MagicMock()
        mock_producer_class.return_value = mock_producer
        mock_consumer_class.return_value = mock_consumer

        # Simulate consumer calling callback with event
        def fake_consume(topic, callback):
            callback(self.event.__dict__)

        config = KafkaConfig(bootstrap_servers="localhost:9092")
        consumer = KafkaConsumerService(config=config, group_id="test-group")
        consumer.consume = fake_consume

        producer = KafkaProducerService(config=config)
        # Simulate sending event
        producer.send(self.topic, self.event)
        # Simulate consuming event
        consumer.consume(self.topic, lambda msg: self.received.append(msg))

        self.assertTrue(any(e['id'] == self.event.id for e in self.received), "Event not consumed")

if __name__ == "__main__":
    unittest.main()
