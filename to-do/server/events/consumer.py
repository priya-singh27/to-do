from kafka import KafkaConsumer
import json
import threading
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

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
    
    def _safe_json_deserializer(self, message_bytes):
        """Safely deserialize a message as JSON, returning None for invalid JSON."""
        if message_bytes is None:
            return None
            
        try:
            message_str = message_bytes.decode('utf-8')
            return json.loads(message_str)
        except json.JSONDecodeError:
            print(f"Skipping non-JSON message: {message_bytes[:50]}...")
            return None
        except Exception as e:
            print(f"Error deserializing message: {str(e)}")
            return None
    
    def _consume(self):
        """Consume events from the Kafka topic."""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                value_deserializer=self._safe_json_deserializer
            )
            
            for message in self.consumer:
                if not self.running:
                    break
                
                # Only process valid JSON messages
                if message.value is not None:
                    try:
                        self.callback(message.value)
                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
        except Exception as e:
            print(f"Error in consumer: {str(e)}")
        finally:
            if self.consumer:
                try:
                    self.consumer.close()
                except Exception as e:
                    print(f"Error closing consumer: {str(e)}")
    
    def stop(self):
        """Stop consuming events."""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                print(f"Error closing consumer during stop: {str(e)}")
        if self.thread:
            self.thread.join(timeout=5)