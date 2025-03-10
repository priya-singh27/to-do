import json
import datetime
from kafka import KafkaProducer
import time
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Configure the producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Create a task due in the near future (30 seconds from now)
# Using timezone-aware objects as recommended by the deprecation warning
current_time = datetime.datetime.now(datetime.UTC)
scheduled_time = (current_time + datetime.timedelta(seconds=30)).isoformat()

# Task creation event
task_event = {
    "event_type": "TaskCreated",
    "task_id": 999,  # Test task ID
    "user_id": 5,
    "scheduled_time": scheduled_time
}

# Send to the correct topic 'task_topic' instead of 'task-events'
topic_name = 'task_topic'  # This should match the topic your application is listening to
future = producer.send(topic_name, task_event)
result = future.get(timeout=60)
print(f"Task creation event sent to {topic_name}, offset: {result.offset}")

print(f"Task scheduled for: {scheduled_time}")
print("Waiting to see if notification gets triggered...")
print("Watching for events in 'task_due_topic'...")

# Wait for a minute to see the task get processed
time.sleep(60)