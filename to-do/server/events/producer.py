from kafka import KafkaProducer
import json
import os

KAFKA_BOOTSTRAP_SERVERS=os.getenv("KAFKA_BOOTSTRAP_SERVERS")

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # retries=5,  # Retry if failure occurs
        # acks="all",  # Ensure message is acknowledged
        # linger_ms=500,  # Reduce batching time
        # request_timeout_ms=60000,  # Increase timeout to 60 seconds
        # max_block_ms=120000,       
        # security_protocol="PLAINTEXT"
    )
except Exception as e:
    print(f"Failed to connect to Kafka: {str(e)}")
    producer = None

def publish_event(topic: str, event_data: dict):
    """Publish an event to Kafka topic."""
    if producer:
        try:
            future = producer.send(topic, event_data)
            future.get(timeout=60)  # Block until a single message is sent
            print(f"Event published to {topic}: {event_data}")
            return True
        except Exception as e:
            print(f"Failed to publish event: {str(e)}")
            return False
    else:
        print("Kafka producer not initialized")
        return False