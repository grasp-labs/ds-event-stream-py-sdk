import unittest
from unittest.mock import patch, MagicMock
from dseventstream.kafka.kafka_service import KafkaProducerService, KafkaConsumerService
from dseventstream.kafka.kafka_config import KafkaConfig
from dseventstream.models.event import Event

class TestKafkaProducerServiceMock(unittest.TestCase):
    @patch('dseventstream.kafka.kafka_service.Producer')
    def test_send_event(self, mock_producer_class):
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="mock:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
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
        producer.send("test-topic", event)
        mock_producer.produce.assert_called()
        mock_producer.flush.assert_called_once()

class TestKafkaConsumerServiceMock(unittest.TestCase):
    @patch('dseventstream.kafka.kafka_service.Consumer')
    def test_consume_event(self, mock_consumer_class):
        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [
            MagicMock(value=lambda: b'{"id": "test-id"}', error=lambda: None),
            None,
            KeyboardInterrupt()
        ]
        mock_consumer_class.return_value = mock_consumer
        config = KafkaConfig(bootstrap_servers="mock:9092")
        consumer = KafkaConsumerService(config=config, group_id="mock-group")
        received = []
        def on_message(msg):
            received.append(msg)
        try:
            consumer.consume("test-topic", on_message)
        except KeyboardInterrupt:
            pass
        self.assertTrue(any('id' in e for e in received))

if __name__ == "__main__":
    unittest.main()
