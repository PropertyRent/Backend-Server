import os
from config.nodemailer import send_email


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "no-reply@example.com")


async def send_contact_confirmation_email(to_email: str, full_name: str):
    """Send confirmation email to user after they submit contact form"""
    subject = "Thank you for contacting us - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Thank you for contacting us!</h2>
        <p>Hi {full_name},</p>
        <p>We have received your message and our team will get back to you as soon as possible.</p>
        <p>We typically respond within 24-48 hours during business days.</p>
        <p>If your inquiry is urgent, please don't hesitate to call us directly.</p>
        <p style="margin-top: 20px;">Best regards,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_contact_notification_to_admin(contact_data: dict):
    """Send notification to admin when new contact message is received"""
    subject = f"New Contact Message from {contact_data['full_name']} - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">New Contact Message</h2>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
          <p><strong>Name:</strong> {contact_data['full_name']}</p>
          <p><strong>Email:</strong> {contact_data['email']}</p>
          <p><strong>Message:</strong></p>
          <div style="background-color: #ffffff; padding: 10px; border-left: 4px solid #1a39ffff;">
            {contact_data['message']}
          </div>
        </div>
        <p><strong>Contact ID:</strong> {contact_data['id']}</p>
        <p><strong>Received:</strong> {contact_data['created_at']}</p>
        <p style="margin-top: 20px;">Please log in to the admin panel to respond to this message.</p>
      </div>
    </div>
    """
    return await send_email(ADMIN_EMAIL, subject, html_content)


async def send_property_search_notification_to_admin(search_data: dict):
    """Send notification to admin when user completes property search via chatbot"""
    subject = f"New Property Search Request from {search_data['email']} - Property-Rent Chatbot"
    
    # Build preferences table
    preferences_html = ""
    for key, value in search_data['preferences'].items():
        preferences_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px; font-weight: bold; color: #333;">{key}:</td>
            <td style="padding: 8px; color: #666;">{value}</td>
        </tr>
        """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 700px; margin: auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 25px;">
          <h2 style="color: #1a39ffff; margin: 0;">🏠 New Property Search Request</h2>
          <p style="color: #666; margin: 5px 0;">Via Chatbot - Property Search Assistant</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #1a39ffff; margin-top: 0;">Customer Information</h3>
          <p><strong>Email:</strong> <a href="mailto:{search_data['email']}" style="color: #1a39ffff;">{search_data['email']}</a></p>
          <p><strong>Session ID:</strong> {search_data['session_id']}</p>
          <p><strong>Completed:</strong> {search_data['completed_at']}</p>
        </div>

        <div style="background-color: #ffffff; border: 2px solid #1a39ffff; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #1a39ffff; margin: 0; padding: 15px; background-color: #f0f4ff; border-radius: 6px 6px 0 0;">Property Requirements</h3>
          <table style="width: 100%; border-collapse: collapse;">
            {preferences_html}
          </table>
        </div>

        <div style="background-color: #e8f4ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
          <h4 style="color: #1a39ffff; margin-top: 0;">📋 Next Steps:</h4>
          <ul style="color: #333; line-height: 1.6;">
            <li>Review the customer's property requirements above</li>
            <li>Search for matching properties in your database</li>
            <li>Contact the customer at <strong>{search_data['email']}</strong></li>
            <li>Provide personalized property recommendations</li>
            <li>Schedule property viewings if interested</li>
          </ul>
        </div>

        <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee;">
          <p style="color: #666; font-size: 14px;">
            This inquiry was generated automatically by the Property-Rent Chatbot System<br/>
            Please respond promptly to maintain customer satisfaction
          </p>
        </div>
      </div>
    </div>
    """
    return await send_email(ADMIN_EMAIL, subject, html_content)


async def send_admin_reply_to_user(to_email: str, full_name: str, admin_reply: str, original_message: str):
    """Send admin reply to user"""
    subject = "Reply to your inquiry - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Reply to your inquiry</h2>
        <p>Hi {full_name},</p>
        <p>Thank you for contacting Property-Rent. Here's our response to your inquiry:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
          <h4 style="color: #1a39ffff; margin-top: 0;">Our Response:</h4>
          <div style="background-color: #ffffff; padding: 10px; border-left: 4px solid #28a745;">
            {admin_reply}
          </div>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
          <h4 style="color: #6c757d; margin-top: 0;">Your Original Message:</h4>
          <div style="background-color: #ffffff; padding: 10px; border-left: 4px solid #6c757d;">
            {original_message}
          </div>
        </div>
        
        <p>If you have any further questions, please don't hesitate to contact us again.</p>
        <p style="margin-top: 20px;">Best regards,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)