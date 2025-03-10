from events.consumer import EventConsumer
from events.producer import publish_event
import time
import threading
import datetime
import json
from typing import Dict, Any
import os

KAFKA_TASK_TOPIC = os.getenv("KAFKA_TASK_TOPIC", "task_topic")
KAFKA_TASK_DUE_TOPIC = os.getenv("KAFKA_TASK_DUE_TOPIC", "task_due_topic")

class SchedulerService:
    def __init__(self):
        self.scheduled_tasks = {}  # task_id -> task_data
        self.consumer = EventConsumer(
            topic=KAFKA_TASK_TOPIC,
            group_id="scheduler-service",
            callback=self.handle_task_event
        )
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start the scheduler service."""
        if self.running:
            return
        
        self.running = True
        
        # Start consuming task events
        self.consumer.start()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        print("Scheduler service started")
    
    def _run_scheduler(self):
        """Check for due tasks and publish TaskDue events."""
        while self.running:
            # Use timezone-aware datetime for proper comparison
            now = datetime.datetime.now(datetime.timezone.utc)
            print(f"Scheduler check at {now}, tasks: {len(self.scheduled_tasks)}")
            due_tasks = []
            
            # Find tasks that are due
            for task_id, task_data in list(self.scheduled_tasks.items()):
                try:
                    scheduled_time_str = task_data["scheduled_time"]
                    
                    # Handle both timezone-aware and naive datetime strings
                    try:
                        # Try parsing with timezone first
                        scheduled_time = datetime.datetime.fromisoformat(scheduled_time_str)
                        # If the parsed datetime has no timezone, assume UTC
                        if scheduled_time.tzinfo is None:
                            scheduled_time = scheduled_time.replace(tzinfo=datetime.UTC)
                    except ValueError:
                        # Fallback for older datetime formats
                        scheduled_time = datetime.datetime.strptime(scheduled_time_str, "%Y-%m-%dT%H:%M:%S.%f")
                        scheduled_time = scheduled_time.replace(tzinfo=datetime.UTC)
                    
                    print(f"Checking task {task_id}: scheduled for {scheduled_time}, now is {now}")
                    
                    # Compare timezone-aware datetimes
                    if now >= scheduled_time:
                        print(f"Task {task_id} is due!")
                        due_tasks.append((task_id, task_data))
                        # Remove from scheduled tasks
                        del self.scheduled_tasks[task_id]
                except Exception as e:
                    print(f"Error checking task {task_id}: {str(e)}")
            
            # Publish TaskDue events for due tasks
            for task_id, task_data in due_tasks:
                event_data = {
                    "event_type": "TaskDue",
                    "task_id": task_id,
                    "user_id": task_data["user_id"],
                    "scheduled_time": task_data["scheduled_time"],
                    "notification_time": datetime.datetime.now(datetime.UTC).isoformat()
                }
                result = publish_event(KAFKA_TASK_DUE_TOPIC, event_data)
                if result:
                    print(f"Successfully published TaskDue event for task {task_id}")
                else:
                    print(f"Failed to publish TaskDue event for task {task_id}")
            
            # Sleep for a while
            time.sleep(10)  # Check every 10 seconds
    
    def handle_task_event(self, event: Dict[str, Any]):
        """Handle task-related events from Kafka."""
        try:
            print(f"Received task event: {event}")
            if not event:
                print("Received empty event, skipping")
                return
                
            event_type = event.get("event_type")
            task_id = event.get("task_id")
            
            if not task_id:
                print("Event missing task_id, skipping")
                return
                
            scheduled_time = event.get("scheduled_time")
            
            if event_type == "TaskCreated" or event_type == "TaskUpdated":
                if scheduled_time:
                    # Schedule the task
                    self.scheduled_tasks[task_id] = {
                        "user_id": event.get("user_id"),
                        "scheduled_time": scheduled_time
                    }
                    print(f"Task {task_id} scheduled for {scheduled_time}")
                    print(f"Current scheduled tasks: {self.scheduled_tasks}")
                else:
                    print(f"Task {task_id} has no scheduled time, not adding to scheduler")
            
            elif event_type == "TaskDeleted":
                # Remove the task from scheduled tasks
                if task_id in self.scheduled_tasks:
                    del self.scheduled_tasks[task_id]
                    print(f"Task {task_id} removed from scheduler")
        except Exception as e:
            print(f"Error handling task event: {str(e)}")
    
    def stop(self):
        """Stop the scheduler service."""
        self.running = False
        if self.consumer:
            self.consumer.stop()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("Scheduler service stopped")