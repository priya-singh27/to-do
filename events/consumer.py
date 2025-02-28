from kafka import KafkaConsumer
import json
import threading
import os

KAFKA_BOOTSTRAP_SERVERS=os.getenv("KAFKA_BOOTSTRAP_SERVERS")

class EventConsumer:
    def __init__(self, topic, group_id, callback):
        self.topic = topic
        self.group_id = group_id
        self.callback = callback
        self.consumer = None
        self.running = False
        self.thread = None
    
    def start(self):
        """Start consuming events in a separate thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._consume)
        self.thread.daemon = True
        self.thread.start()
    
    def _consume(self):
        """Consume events from the Kafka topic."""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            for message in self.consumer:
                if not self.running:
                    break
                self.callback(message.value)
        except Exception as e:
            print(f"Error in consumer: {str(e)}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def stop(self):
        """Stop consuming events."""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.thread:
            self.thread.join(timeout=5)