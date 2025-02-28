from events.consumer import EventConsumer
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, Any

KAFKA_TASK_DUE_TOPIC=os.getenv("KAFKA_TASK_DUE_TOPIC")
SENDGRID_API_KEY= os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL=os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_TEMPLATE_ID=os.getenv("SENDGRID_TEMPLATE_ID")

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
    
    def send_email_notification(self, task_id: int, user_id: int, scheduled_time: str):
        """Send email notification using SendGrid."""
        try:
            if not SENDGRID_API_KEY:
                print("SendGrid API key not configured")
                return False
            
            # In a real application, you would fetch the user's email from the database
            # For simplicity, we'll assume we have it
            recipient_email = "user@example.com"  # This should be fetched from a user service
            
            message = Mail(
                from_email=SENDGRID_FROM_EMAIL,
                to_emails=recipient_email,
                subject='Task Due Notification',
            )
            
            # Set template ID
            message.template_id = SENDGRID_TEMPLATE_ID
            
            # Add template data
            message.dynamic_template_data = {
                'task_id': task_id,
                'scheduled_time': scheduled_time,
                'user_id': user_id
            }
            
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