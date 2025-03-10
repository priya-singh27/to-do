from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

SENDGRID_API_KEY= os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL=os.getenv("SENDGRID_FROM_EMAIL")

def send_email(to_email, subject, content, template_id=None, template_data=None):
    """Send an email using SendGrid."""
    if not SENDGRID_API_KEY :
        print("SendGrid API key not configured")
        return False
    
    message = Mail(
        from_email= SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
    )
    
    if template_id:
        message.template_id = template_id
        if template_data:
            message.dynamic_template_data = template_data
    else:
        message.content = content
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent with status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False