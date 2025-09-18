"""
kafka_config.py
Shared config for Kafka service principals (producer/consumer)
"""

from typing import Dict

class KafkaConfig:
    def __init__(self, bootstrap_servers: str, username: str = None, password: str = None, extra: Dict = None):
        self.bootstrap_servers = bootstrap_servers
        self.username = username
        self.password = password
        # Hardcoded values for your instance
        self.security_protocol = "SASL_PLAINTEXT"
        self.sasl_mechanism = "SCRAM-SHA-512"
        self.extra = extra or {}

    def to_dict(self):
        config = {
            'bootstrap.servers': self.bootstrap_servers
        }
        if self.security_protocol:
            config['security.protocol'] = self.security_protocol
        if self.sasl_mechanism:
            config['sasl.mechanism'] = self.sasl_mechanism
        if self.username:
            config['sasl.username'] = self.username
        if self.password:
            config['sasl.password'] = self.password
        config.update(self.extra)
        return config
