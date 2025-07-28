import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import os

class EmailService:
    def __init__(self):
        # Email configuration - these should be set in Streamlit secrets or environment variables
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
    
    def send_email(self, recipient_email, recipient_name, subject, body):
        """Send an email to a recipient"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create HTML and plain text versions
            text = body
            html = f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                  <h2 style="color: #1f77b4;">🎮 Event Results</h2>
                  <div style="white-space: pre-line;">{body}</div>
                  <br>
                  <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                      This email was sent from the Event Tracker System.<br>
                      Thank you for participating! 🎉
                    </p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            
            # Add HTML/plain-text parts to MIMEMultipart message
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            return True
            
        except Exception as e:
            st.error(f"Error sending email to {recipient_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, recipients_df, subject, body_template):
        """Send emails to multiple recipients"""
        success_count = 0
        failed_emails = []
        
        for _, recipient in recipients_df.iterrows():
            # Personalize the email body
            personalized_body = body_template.format(
                name=recipient.get('name', 'Participant'),
                total_score=recipient.get('total', 0),
                gift_type=recipient.get('gift_type', 'Participation'),
                emp_id=recipient.get('emp_id', ''),
                department=recipient.get('department', '')
            )
            
            # Send email
            if self.send_email(
                recipient.get('email', ''),
                recipient.get('name', ''),
                subject,
                personalized_body
            ):
                success_count += 1
            else:
                failed_emails.append(recipient.get('email', ''))
        
        return success_count, failed_emails
    
    def validate_email_config(self):
        """Validate email configuration"""
        if not self.sender_email or not self.sender_password:
            return False, "Email credentials not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in environment variables or Streamlit secrets."
        
        try:
            # Test connection
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
            return True, "Email configuration is valid."
        
        except Exception as e:
            return False, f"Email configuration error: {str(e)}"
    
    def get_email_templates(self):
        """Get predefined email templates"""
        templates = {
            "Score Notification": {
                "subject": "🎮 Your Event Score Results!",
                "body": """Dear {name},

Congratulations on participating in our exciting gaming event! 🎉

Here are your results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {name}
🆔 Employee ID: {emp_id}
📊 Total Score: {total_score} points
🎁 Gift Category: {gift_type}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for your enthusiasm and participation! Your performance was amazing.

Best regards,
Event Organizing Team"""
            },
            
            "Winner Announcement": {
                "subject": "🏆 Congratulations - You're a Winner!",
                "body": """Dear {name},

🎉 CONGRATULATIONS! 🎉

We are thrilled to announce that you have won in our gaming event!

Your Achievement:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Gift Category: {gift_type}
📊 Your Score: {total_score} points
🎯 Your Performance: Outstanding!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please collect your gift from the organizing team.

Once again, congratulations on your excellent performance! 🌟

Best regards,
Event Organizing Team"""
            },
            
            "Participation Certificate": {
                "subject": "🎁 Thank You for Your Participation!",
                "body": """Dear {name},

Thank you for being part of our amazing gaming event! 🎮

Your Participation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {name}
📊 Your Score: {total_score} points
🎁 Recognition: {gift_type} Gift
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every participant is a winner in our eyes! Your enthusiasm and participation made this event a huge success.

Please collect your participation gift from the organizing team.

Thank you once again! 🎉

Best regards,
Event Organizing Team"""
            }
        }
        
        return templates
    
    def create_custom_template(self, template_name, subject, body):
        """Create a custom email template"""
        return {
            template_name: {
                "subject": subject,
                "body": body
            }
        }
    
    def preview_email(self, template, sample_data):
        """Preview an email with sample data"""
        try:
            subject = template["subject"]
            body = template["body"].format(**sample_data)
            
            return subject, body
        except KeyError as e:
            return None, f"Template error: Missing placeholder {str(e)}"
        except Exception as e:
            return None, f"Preview error: {str(e)}"
