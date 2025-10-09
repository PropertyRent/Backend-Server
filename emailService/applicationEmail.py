from config.nodemailer import send_email

async def send_application_confirmation(to_email: str, application_data: dict):
    """Send confirmation email to user when application is submitted"""
    subject = "Application Received - Property-Rent"
    
    application_id = application_data.get('application_id')
    full_name = application_data.get('full_name', 'Applicant')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #28a745;">Application Received Successfully!</h2>
        <p>Dear {full_name},</p>
        <p>Thank you for submitting your rental application. We have received your application and it's now under review.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
          <h3>Application Details:</h3>
          <p><strong>Application ID:</strong> {application_id}</p>
          <p><strong>Status:</strong> Pending Review</p>
          <p><strong>Submitted:</strong> {application_data.get('submitted_date', 'Today')}</p>
        </div>
        
        <p><strong>What's Next?</strong></p>
        <ul>
          <li>Our team will review your application within 2-3 business days</li>
          <li>We may contact you for additional information if needed</li>
          <li>You'll receive an email notification with our decision</li>
        </ul>
        
        <p>If you have any questions, please don't hesitate to contact us.</p>
        
        <p style="margin-top: 20px;">Best regards,<br>Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def send_admin_reply_to_application(to_email: str, application_data: dict):
    """Send admin reply to user about their application"""
    subject = f"Update on Your Application - Property-Rent"
    
    application_id = application_data.get('application_id')
    full_name = application_data.get('full_name', 'Applicant')
    admin_reply = application_data.get('admin_reply', '')
    status = application_data.get('status', 'pending')
    admin_name = application_data.get('admin_name', 'Admin')
    
    # Status colors
    status_colors = {
        'pending': '#ffc107',
        'reviewed': '#17a2b8', 
        'approved': '#28a745',
        'rejected': '#dc3545',
        'completed': '#6c757d'
    }
    status_color = status_colors.get(status.lower(), '#6c757d')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: {status_color};">Application Update</h2>
        <p>Dear {full_name},</p>
        <p>We have an update regarding your rental application:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid {status_color}; margin: 20px 0;">
          <h3>Application Details:</h3>
          <p><strong>Application ID:</strong> {application_id}</p>
          <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status.title()}</span></p>
        </div>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h4 style="color: #1976d2;">Message from our team:</h4>
          <p style="font-style: italic;">"{admin_reply}"</p>
          <p style="text-align: right; margin-top: 10px; color: #666;">- {admin_name}</p>
        </div>
        
        <p>If you have any questions about your application, please feel free to contact us.</p>
        
        <p style="margin-top: 20px;">Best regards,<br>Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def send_application_status_update(to_email: str, application_data: dict):
    """Send status update email to user"""
    subject = f"Application {application_data.get('status', '').title()} - Property-Rent"
    
    application_id = application_data.get('application_id')
    full_name = application_data.get('full_name', 'Applicant')
    status = application_data.get('status', 'pending')
    
    # Status-specific content
    status_messages = {
        'reviewed': {
            'color': '#17a2b8',
            'title': 'Application Under Review',
            'message': 'Your application is now being reviewed by our team. We will contact you soon with next steps.'
        },
        'approved': {
            'color': '#28a745',
            'title': 'Application Approved!',
            'message': 'Congratulations! Your rental application has been approved. We will contact you soon to proceed with the lease agreement.'
        },
        'rejected': {
            'color': '#dc3545',
            'title': 'Application Update',
            'message': 'Thank you for your interest. Unfortunately, we are unable to approve your application at this time.'
        },
        'completed': {
            'color': '#6c757d',
            'title': 'Application Completed',
            'message': 'Your rental application process has been completed. Welcome to your new home!'
        }
    }
    
    status_info = status_messages.get(status.lower(), {
        'color': '#6c757d',
        'title': 'Application Update',
        'message': f'Your application status has been updated to: {status.title()}'
    })
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: {status_info['color']};">{status_info['title']}</h2>
        <p>Dear {full_name},</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid {status_info['color']}; margin: 20px 0;">
          <h3>Application Details:</h3>
          <p><strong>Application ID:</strong> {application_id}</p>
          <p><strong>Status:</strong> <span style="color: {status_info['color']}; font-weight: bold;">{status.title()}</span></p>
        </div>
        
        <p>{status_info['message']}</p>
        
        <p>If you have any questions, please don't hesitate to contact us.</p>
        
        <p style="margin-top: 20px;">Best regards,<br>Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)

async def notify_admin_new_application(admin_email: str, application_data: dict):
    """Notify admin about new application submission"""
    subject = "New Rental Application Submitted"
    
    application_id = application_data.get('application_id')
    full_name = application_data.get('full_name', 'Unknown')
    email = application_data.get('email', 'Not provided')
    phone = application_data.get('phone_number', 'Not provided')
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #007bff;">New Rental Application</h2>
        <p>A new rental application has been submitted and requires review.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
          <h3>Applicant Information:</h3>
          <p><strong>Name:</strong> {full_name}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Phone:</strong> {phone}</p>
          <p><strong>Application ID:</strong> {application_id}</p>
          <p><strong>Submitted:</strong> {application_data.get('submitted_date', 'Today')}</p>
        </div>
        
        <a href="#" style="
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
        ">Review Application</a>
        
        <p style="margin-top: 20px;">Property-Rent Admin System</p>
      </div>
    </div>
    """
    return await send_email(admin_email, subject, html_content)