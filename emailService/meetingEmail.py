import os
from config.nodemailer import send_email
from datetime import datetime

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "no-reply@example.com")

async def send_meeting_request_confirmation(to_email: str, meeting_data: dict):
    """Send confirmation email to user when meeting is requested"""
    subject = "Meeting Request Received - Property-Rent"
    
    # Format date and time for display
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Meeting Request Received</h2>
        <p>Dear {full_name},</p>
        <p>Thank you for your interest in our property. We have received your meeting request with the following details:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h3 style="color: #4733fcff; margin-top: 0;">Meeting Details</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Date:</strong> {meeting_date}</p>
          <p><strong>Time:</strong> {meeting_time}</p>
          <p><strong>Status:</strong> Pending Approval</p>
        </div>
        
        <p>Our team will review your request and get back to you within 24 hours with confirmation details.</p>
        <p>You can track the status of your meeting request by logging into your account.</p>
        
        <a href="{FRONTEND_URL}/dashboard" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">View My Meetings</a>
        
        <p style="margin-top: 20px;">If you have any questions, please don't hesitate to contact us.</p>
        <p>Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def send_meeting_approval_email(to_email: str, meeting_data: dict):
    """Send approval email to user when meeting is approved by admin"""
    subject = "Meeting Approved - Property-Rent"
    
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    admin_notes = meeting_data.get('admin_notes', '')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #28a745;">Meeting Approved!</h2>
        <p>Dear {full_name},</p>
        <p>Great news! Your meeting request has been approved by our team.</p>
        
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
          <h3 style="color: #155724; margin-top: 0;">Confirmed Meeting Details</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Date:</strong> {meeting_date}</p>
          <p><strong>Time:</strong> {meeting_time}</p>
          <p><strong>Status:</strong> <span style="color: #28a745;">Approved</span></p>
        </div>
        
        {f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;"><h4>Message from Admin:</h4><p>{meeting_data.get("admin_reply", admin_notes)}</p></div>' if meeting_data.get("admin_reply") or admin_notes else ''}
        
        <p><strong>What to bring:</strong></p>
        <ul>
          <li>Valid photo ID</li>
          <li>Proof of income (if interested in applying)</li>
          <li>Any questions you'd like to discuss</li>
        </ul>
        
        <p>Please arrive on time for your scheduled appointment. If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
        
        <a href="{FRONTEND_URL}/dashboard" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #28a745;
            text-decoration: none;
            border-radius: 5px;
        ">View Meeting Details</a>
        
        <p style="margin-top: 20px;">We look forward to meeting with you!</p>
        <p>Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def send_meeting_rejection_email(to_email: str, meeting_data: dict):
    """Send rejection email to user when meeting is rejected by admin"""
    subject = "Meeting Request Update - Property-Rent"
    
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    admin_notes = meeting_data.get('admin_notes', 'Unfortunately, we cannot accommodate your meeting request at this time.')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #dc3545;">Meeting Request Update</h2>
        <p>Dear {full_name},</p>
        <p>Thank you for your interest in our property. We have reviewed your meeting request for the following:</p>
        
        <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
          <h3 style="color: #721c24; margin-top: 0;">Meeting Request Details</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Requested Date:</strong> {meeting_date}</p>
          <p><strong>Requested Time:</strong> {meeting_time}</p>
          <p><strong>Status:</strong> <span style="color: #dc3545;">Unable to Schedule</span></p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h4>Message from our team:</h4>
          <p>{meeting_data.get("admin_reply", admin_notes)}</p>
        </div>
        
        <p>We encourage you to:</p>
        <ul>
          <li>Submit a new meeting request for different dates/times</li>
          <li>Contact us directly to discuss alternative options</li>
          <li>Browse other available properties that might interest you</li>
        </ul>
        
        <a href="{FRONTEND_URL}/properties" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">Browse Properties</a>
        
        <p style="margin-top: 20px;">Thank you for your understanding.</p>
        <p>Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def send_meeting_completion_email(to_email: str, meeting_data: dict):
    """Send completion email to user when meeting is marked as completed"""
    subject = "Thank You for Your Visit - Property-Rent"
    
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    meeting_date = meeting_data.get('meeting_date')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #4733fcff;">Thank You for Your Visit!</h2>
        <p>Dear {full_name},</p>
        <p>Thank you for taking the time to visit our property: {property_title} on {meeting_date}.</p>
        
        <p>We hope you found the tour informative and that the property meets your needs. If you're interested in moving forward with an application or have any questions, please don't hesitate to reach out.</p>
        
        <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h3 style="color: #0066cc; margin-top: 0;">Next Steps</h3>
          <ul>
            <li>Submit an application if you're interested</li>
            <li>Contact us with any questions</li>
            <li>Browse our other available properties</li>
          </ul>
        </div>
        
        <a href="{FRONTEND_URL}/properties" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">View More Properties</a>
        
        <p style="margin-top: 20px;">We appreciate your interest and look forward to helping you find your perfect home.</p>
        <p>Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def notify_admin_new_meeting(admin_email: str, meeting_data: dict):
    """Notify admin when a new meeting is scheduled"""
    subject = "New Meeting Request - Property-Rent Admin"
    
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    email = meeting_data.get('email')
    phone = meeting_data.get('phone')
    message = meeting_data.get('message', 'No additional message')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #ff8c00;">New Meeting Request</h2>
        <p>A new meeting has been scheduled and requires your review.</p>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ff8c00;">
          <h3 style="color: #856404; margin-top: 0;">Meeting Details</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Client:</strong> {full_name}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Phone:</strong> {phone}</p>
          <p><strong>Requested Date:</strong> {meeting_date}</p>
          <p><strong>Requested Time:</strong> {meeting_time}</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h4>Client Message:</h4>
          <p>{message}</p>
        </div>
        
        <p>Please review and approve/reject this meeting request.</p>
        
        <a href="{FRONTEND_URL}/admin/meetings" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #ff8c00;
            text-decoration: none;
            border-radius: 5px;
        ">Review Meeting Request</a>
        
        <p style="margin-top: 20px;">Property-Rent Admin System</p>
      </div>
    </div>
    """
    return await send_email(admin_email, subject, html_content)


async def send_admin_reply_email(to_email: str, meeting_data: dict):
    """Send admin reply to user when admin sends a message without changing status"""
    subject = "Message from Admin - Property-Rent"
    
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    admin_message = meeting_data.get('admin_message', '')
    admin_name = meeting_data.get('admin_name', 'Admin')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #007bff;">Message from Property Admin</h2>
        <p>Dear {full_name},</p>
        <p>You have received a message from our admin regarding your meeting request:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
          <h3>Meeting Details:</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Date:</strong> {meeting_date}</p>
          <p><strong>Time:</strong> {meeting_time}</p>
        </div>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h4 style="color: #1976d2;">Admin Message:</h4>
          <p style="font-style: italic;">"{admin_message}"</p>
          <p style="text-align: right; margin-top: 10px; color: #666;">- {admin_name}</p>
        </div>
        
        <p>If you have any questions or need to make changes to your meeting, please feel free to contact us.</p>
        
        <p style="margin-top: 20px;">Best regards,<br>Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_meeting_cancellation_email(to_email: str, meeting_data: dict):
    """Send cancellation email to user when admin deletes a meeting"""
    subject = "Meeting Cancelled - Property-Rent"
    
    meeting_date = meeting_data.get('meeting_date')
    meeting_time = meeting_data.get('meeting_time')
    property_title = meeting_data.get('property_title', 'Property')
    full_name = meeting_data.get('full_name')
    admin_name = meeting_data.get('admin_name', 'Admin')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #dc3545;">Meeting Cancelled</h2>
        <p>Dear {full_name},</p>
        <p>We regret to inform you that your meeting request has been cancelled by our admin team.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
          <h3>Cancelled Meeting Details:</h3>
          <p><strong>Property:</strong> {property_title}</p>
          <p><strong>Date:</strong> {meeting_date}</p>
          <p><strong>Time:</strong> {meeting_time}</p>
        </div>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
          <h4 style="color: #856404;">What's Next?</h4>
          <p>You can schedule a new meeting at any time through our website.</p>
          <p>If you have any questions about this cancellation, please don't hesitate to contact us.</p>
        </div>
        
        <p>We apologize for any inconvenience caused and appreciate your understanding.</p>
        
        <p style="margin-top: 20px;">Best regards,<br>Property-Rent Team<br><small>Cancelled by: {admin_name}</small></p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)