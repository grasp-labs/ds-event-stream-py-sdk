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

if __name__ == "__main__":
    unittest.main()
