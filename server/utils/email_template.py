# utils/email_templates.py
def get_task_reminder_template():
    """Returns the HTML template for task reminder emails."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333333;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f7f7f7; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #4a69bd; padding: 30px 40px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">Task Reminder</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin-top: 0; font-size: 16px;">Hello,</p>
                                
                                <p style="font-size: 16px;">This is a friendly reminder about your pending to-do task. Please review the details below and ensure timely completion.</p>
                                
                                <table width="100%" style="border-collapse: collapse; margin: 25px 0; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <tr>
                                        <th colspan="2" style="background-color: #f1f2f6; color: #333; padding: 15px; text-align: left; font-size: 18px; border-bottom: 1px solid #dfe4ea;">
                                            Task Details
                                        </th>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 15px; border-bottom: 1px solid #dfe4ea; width: 120px; font-weight: bold;">Task Name:</td>
                                        <td style="padding: 12px 15px; border-bottom: 1px solid #dfe4ea;">{task_name}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 15px; border-bottom: 1px solid #dfe4ea; font-weight: bold;">Due Date:</td>
                                        <td style="padding: 12px 15px; border-bottom: 1px solid #dfe4ea;">{due_date}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 15px; vertical-align: top; font-weight: bold;">Description:</td>
                                        <td style="padding: 12px 15px;">{description}</td>
                                    </tr>
                                </table>
                                
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href="#" style="display: inline-block; background-color: #4a69bd; color: white; text-decoration: none; padding: 12px 25px; border-radius: 4px; font-weight: bold; font-size: 16px;">Open App</a>
                                </div>
                                
                                <p style="font-size: 16px;">Thank you for using our Todo App!</p>
                                
                                <p style="font-size: 16px; margin-bottom: 0;">Best regards,<br>The Todo App Team</p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f1f2f6; padding: 20px 40px; text-align: center; color: #666; font-size: 14px;">
                                <p style="margin: 0;">This is an automated reminder. Please do not reply to this email.</p>
                                <p style="margin: 10px 0 0;">© 2025 Todo App. All rights reserved.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def format_task_reminder_email(task_name, due_date, description):
    """
    Format the task reminder email template with provided values.
    
    Args:
        task_name (str): Name of the task
        due_date (str): Formatted due date
        description (str): Task description
        
    Returns:
        str: Formatted HTML email content
    """
    # Provide default value for empty description
    description = description or "No description provided"
    
    template = get_task_reminder_template()
    
    # Format the template with variables
    formatted_html = template.format(
        task_name=task_name,
        due_date=due_date,
        description=description
    )
    
    return formatted_html