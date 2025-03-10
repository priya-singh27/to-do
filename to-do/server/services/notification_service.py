from events.consumer import EventConsumer
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, Any
from database.db import SessionLocal
from models.user import User
from models.task import Task
from datetime import datetime
import pytz
from utils.email_template import format_task_reminder_email  # Import our new template function

KAFKA_TASK_DUE_TOPIC = os.getenv("KAFKA_TASK_DUE_TOPIC")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

class NotificationService:
    def __init__(self):
        self.consumer = EventConsumer(
            topic=KAFKA_TASK_DUE_TOPIC,
            group_id="notification-service",
            callback=self.handle_task_due_event
        )
    
    def start(self):
        """Start the notification service."""
        self.consumer.start()
        print("Notification service started")
    
    def handle_task_due_event(self, event: Dict[str, Any]):
        """Handle TaskDue events from Kafka."""
        if event.get("event_type") == "TaskDue":
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            scheduled_time = event.get("scheduled_time")
            
            # Send email notification
            self.send_email_notification(task_id, user_id, scheduled_time)
            
            print(f"Notification sent for task {task_id}")
    
    def convert_to_ist(self, time_str: str) -> str:
        """Convert UTC time string to IST formatted time string."""
        try:
            # Parse the ISO format datetime string to a datetime object
            utc_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            # If datetime has no timezone, assume UTC
            if utc_time.tzinfo is None:
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                
            # Convert to IST
            ist_time = utc_time.astimezone(IST)
            
            # Format the datetime in a user-friendly way
            formatted_time = ist_time.strftime("%d %b %Y, %I:%M %p IST")
            return formatted_time
        except Exception as e:
            print(f"Error converting time to IST: {str(e)}")
            return time_str  # Return original string if conversion fails
    
    def send_email_notification(self, task_id: int, user_id: int, scheduled_time: str):
        """Send beautiful email notification using SendGrid."""
        try:
            if not SENDGRID_API_KEY:
                print("SendGrid API key not configured")
                return False
                
            db = SessionLocal()
            try:
                # Get user information
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    print(f"User {user_id} not found")
                    return False
                
                # Get task information
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    print(f"Task {task_id} not found")
                    return False
                    
                recipient_email = user.email
                
                # Convert time to IST
                ist_time = self.convert_to_ist(scheduled_time)
                
                # Get task details
                task_name = task.title
                task_description = task.description
                
            finally:
                db.close()
                
            # Create email subject
            subject = f"Reminder: Your Pending To-Do Task - {task_name}!"
            
            # Use the template formatter from utils
            html_content = format_task_reminder_email(
                task_name=task_name,
                due_date=ist_time,
                description=task_description
            )
            
            # Create email message
            message = Mail(
                from_email=SENDGRID_FROM_EMAIL,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Send the email
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                response = sg.send(message)
                print(f"Email sent with status code: {response.status_code}")
                return True
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Error preparing email: {str(e)}")
            return False
    
    def stop(self):
        """Stop the notification service."""
        if self.consumer:
            self.consumer.stop()
        print("Notification service stopped")