import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import List, Dict, Any
from datetime import datetime
import os
from config.nodemailer import smtp_server, smtp_port, email_user, email_password


async def send_escalation_notification(
    admin_email: str,
    conversation_data: Dict[str, Any],
    messages: List[Dict[str, Any]],
    escalation_reason: str = "unsatisfied"
):
    """Send email notification to admin about escalated conversation"""
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f"🚨 Chatbot Escalation - {escalation_reason.title()}"
        msg['From'] = formataddr(("Property Assistant", email_user))
        msg['To'] = admin_email

        # Format conversation messages
        conversation_html = ""
        for i, message in enumerate(messages, 1):
            question = message.get('question', 'No question')
            answer = message.get('answer', 'No response')
            response_time = message.get('response_time', 0)
            
            conversation_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 3px solid #007bff; background-color: #f8f9fa;">
                <h4 style="color: #007bff; margin: 0 0 10px 0;">Step {i}</h4>
                <p style="margin: 5px 0;"><strong>Question:</strong> {question}</p>
                <p style="margin: 5px 0;"><strong>User Response:</strong> {answer}</p>
                {f'<p style="margin: 5px 0; color: #6c757d;"><small>Response Time: {response_time} seconds</small></p>' if response_time else ''}
            </div>
            """

        # Email HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chatbot Escalation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">🚨 Chatbot Escalation</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">A user needs additional assistance</p>
            </div>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                <h2 style="color: #dc3545; margin-top: 0;">Escalation Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 30%;">Session ID:</td>
                        <td style="padding: 8px 0;">{conversation_data.get('session_id', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Reason:</td>
                        <td style="padding: 8px 0;">{escalation_reason.title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Flow Type:</td>
                        <td style="padding: 8px 0;">{conversation_data.get('flow_type', 'Unknown').replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">User Name:</td>
                        <td style="padding: 8px 0;">{conversation_data.get('user_name', 'Anonymous')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">User Email:</td>
                        <td style="padding: 8px 0;">{conversation_data.get('user_email', 'Not provided')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Started:</td>
                        <td style="padding: 8px 0;">{conversation_data.get('created_at', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Total Messages:</td>
                        <td style="padding: 8px 0;">{len(messages)}</td>
                    </tr>
                </table>
            </div>

            <div style="margin-bottom: 30px;">
                <h2 style="color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;">Full Conversation</h2>
                {conversation_html}
            </div>

            <div style="background-color: #e9ecef; padding: 20px; border-radius: 8px; text-align: center;">
                <h3 style="color: #495057; margin-top: 0;">Next Steps</h3>
                <p style="margin: 10px 0;">Please review this conversation and reach out to the user if needed.</p>
                <p style="margin: 10px 0;">You can view more details in your admin dashboard.</p>
            </div>

            <div style="margin-top: 30px; text-align: center; color: #6c757d; font-size: 14px;">
                <p>This is an automated message from your Property Management System</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """

        msg.set_content(html_content, subtype='html')

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)

        print(f"✅ Escalation email sent to {admin_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send escalation email: {e}")
        return False


async def send_satisfaction_summary(
    admin_email: str,
    conversation_data: Dict[str, Any],
    messages: List[Dict[str, Any]],
    is_satisfied: bool = True
):
    """Send email summary of satisfied conversation to admin"""
    try:
        # Create email message
        subject = "✅ Satisfied Customer - Chatbot Success" if is_satisfied else "❌ Unsatisfied Customer - Needs Review"
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = formataddr(("Property Assistant", email_user))
        msg['To'] = admin_email

        # Format conversation summary (shorter for satisfied customers)
        if is_satisfied:
            summary_html = f"""
            <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #155724; margin-top: 0;">🎉 Customer Successfully Assisted</h3>
                <p><strong>Flow Type:</strong> {conversation_data.get('flow_type', 'Unknown').replace('_', ' ').title()}</p>
                <p><strong>Total Questions:</strong> {len(messages)}</p>
                <p><strong>User:</strong> {conversation_data.get('user_name', 'Anonymous')} ({conversation_data.get('user_email', 'Not provided')})</p>
            </div>
            """
        else:
            # Full conversation for unsatisfied
            conversation_html = ""
            for i, message in enumerate(messages, 1):
                conversation_html += f"""
                <div style="margin-bottom: 15px; padding: 10px; border-left: 2px solid #ffc107; background-color: #fff3cd;">
                    <p><strong>Q{i}:</strong> {message.get('question', 'No question')}</p>
                    <p><strong>A{i}:</strong> {message.get('answer', 'No response')}</p>
                </div>
                """
            
            summary_html = f"""
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #721c24; margin-top: 0;">⚠️ Customer Needs Additional Help</h3>
                <p><strong>Flow Type:</strong> {conversation_data.get('flow_type', 'Unknown').replace('_', ' ').title()}</p>
                <p><strong>User:</strong> {conversation_data.get('user_name', 'Anonymous')} ({conversation_data.get('user_email', 'Not provided')})</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h4>Full Conversation:</h4>
                {conversation_html}
            </div>
            """

        # Email HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chatbot Summary</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, {'#28a745' if is_satisfied else '#dc3545'} 0%, {'#20c997' if is_satisfied else '#c82333'} 100%); color: white; padding: 30px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 24px;">Chatbot Interaction Summary</h1>
            </div>

            {summary_html}

            <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px;">
                <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">
                    Session ID: {conversation_data.get('session_id', 'Unknown')}
                </p>
                <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">
                    Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """

        msg.set_content(html_content, subtype='html')

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)

        print(f"✅ Satisfaction summary email sent to {admin_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send satisfaction summary email: {e}")
        return False