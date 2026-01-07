import unittest
from unittest.mock import MagicMock, patch
from dseventstream.models.event import Event
from dseventstream.kafka.kafka_service import KafkaProducerService
from dseventstream.kafka.kafka_config import KafkaConfig

class TestKafkaProducerService(unittest.TestCase):
    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_send_event(self, mock_producer_class):
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
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
        # Should not raise, and should call mock producer
        producer.send("test-topic", event)
        mock_producer.produce.assert_called()
        mock_producer.flush.assert_called()

    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_validate_with_valid_event_source(self, mock_producer_class):
        """Test that validate returns True when event_source is populated"""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
            id="test-id",
            session_id="test-session",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="valid-source",
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        result = producer.validate(event)
        self.assertTrue(result)

    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_validate_with_empty_event_source(self, mock_producer_class):
        """Test that validate returns False when event_source is empty string"""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
            id="test-id",
            session_id="test-session",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="",
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        result = producer.validate(event)
        self.assertFalse(result)

    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_validate_with_whitespace_only_event_source(self, mock_producer_class):
        """Test that validate returns False when event_source is only whitespace"""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
            id="test-id",
            session_id="test-session",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="   ",
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        result = producer.validate(event)
        self.assertFalse(result)

    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_send_does_not_send_when_validation_fails(self, mock_producer_class):
        """Test that send does not call producer when validation fails"""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
            id="test-id",
            session_id="test-session",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="",  # Empty event_source
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        producer.send("test-topic", event)
        # Producer should NOT be called when validation fails
        mock_producer.produce.assert_not_called()
        mock_producer.flush.assert_not_called()

    @patch("dseventstream.kafka.kafka_service.Producer")
    def test_send_calls_producer_when_validation_passes(self, mock_producer_class):
        """Test that send calls producer when validation passes"""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        producer = KafkaProducerService(config=config)
        event = Event(
            id="test-id",
            session_id="test-session",
            tenant_id="test-tenant",
            event_type="test-type",
            event_source="valid-source",
            timestamp="2025-09-18T00:00:00Z",
            created_by="tester",
            md5_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        producer.send("test-topic", event)
        # Producer SHOULD be called when validation passes
        mock_producer.produce.assert_called()
        mock_producer.flush.assert_called()

if __name__ == "__main__":
    unittest.main()
