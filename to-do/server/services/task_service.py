from sqlalchemy.orm import Session
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate
from events.producer import publish_event
from datetime import datetime, timedelta
from typing import List, Optional
import os

# Define the IST offset (+5:30)
IST_OFFSET = timedelta(hours=5, minutes=30)
KAFKA_TASK_TOPIC = os.getenv("KAFKA_TASK_TOPIC")

class TaskService:    
    
    def create_task(self, db: Session, task: TaskCreate, user_id: int):
        scheduled_time_utc = None
        if task.scheduled_time:
            if task.scheduled_time.tzinfo:
                scheduled_time_utc = task.scheduled_time
            else:
                scheduled_time_utc = task.scheduled_time - IST_OFFSET
        
        db_task = Task(
            title=task.title,
            description=task.description,
            scheduled_time=scheduled_time_utc,
            user_id=user_id
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Publish task created event to Kafka
        event_data = {
            "event_type": "TaskCreated",
            "task_id": db_task.id,
            "user_id": user_id,
            "scheduled_time": db_task.scheduled_time.isoformat() if db_task.scheduled_time else None
        }
        publish_event(KAFKA_TASK_TOPIC, event_data)
        
        return db_task
    
    def get_task(self, db: Session, task_id: int, user_id: int):
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if task and task.scheduled_time:
            # Convert UTC to IST for display by adding the IST offset
            task.scheduled_time = task.scheduled_time + IST_OFFSET
        return task
    
    def get_tasks(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        tasks = db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()
        for task in tasks:
            if task.scheduled_time:
                # Convert UTC to IST for display by adding the IST offset
                task.scheduled_time = task.scheduled_time + IST_OFFSET
        return tasks
    
    def update_task(self, db: Session, task_id: int, task_update: TaskUpdate, user_id: int):
        db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if db_task:
            update_data = task_update.dict(exclude_unset=True)
            
            # Handle scheduled_time conversion if it's being updated
            if 'scheduled_time' in update_data and update_data['scheduled_time']:
                scheduled_time = update_data['scheduled_time']
                if scheduled_time.tzinfo:
                    # If it has timezone info, use it as is
                    update_data['scheduled_time'] = scheduled_time
                else:
                    # If it's timezone naive, assume it's in IST and convert to UTC
                    update_data['scheduled_time'] = scheduled_time - IST_OFFSET
            
            for key, value in update_data.items():
                setattr(db_task, key, value)
            
            db_task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_task)
            
            # Publish task updated event to Kafka
            event_data = {
                "event_type": "TaskUpdated",
                "task_id": db_task.id,
                "user_id": user_id,
                "scheduled_time": db_task.scheduled_time.isoformat() if db_task.scheduled_time else None
            }
            publish_event(KAFKA_TASK_TOPIC, event_data)
            
            return db_task
        return None
    
    def delete_task(self, db: Session, task_id: int, user_id: int):
        db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            
            # Publish task deleted event to Kafka
            event_data = {
                "event_type": "TaskDeleted",
                "task_id": task_id,
                "user_id": user_id
            }
            publish_event(KAFKA_TASK_TOPIC, event_data)
            
            return True
        return False