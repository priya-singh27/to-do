from kafka import KafkaProducer
import json
import time

# Basic producer configuration with detailed debugging
producer = KafkaProducer(
    bootstrap_servers="23.94.253.229:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    max_request_size=1000,  # Limit request size
    compression_type="gzip"  # Use compression to keep packets smaller
)


# Test message
message = {"test": "simple"}

try:
    print("Sending minimal message...")
    future = producer.send("task_topic", message)
    record_metadata = future.get(timeout=30)
    print(f"Success! Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
finally:
    producer.close()