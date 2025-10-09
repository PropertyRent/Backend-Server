import os
from datetime import datetime
from config.nodemailer import send_email


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "no-reply@example.com")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Property-Rent")


async def send_maintenance_request_to_contractor(maintenance_data: dict, additional_message: str = None):
    """Send maintenance request details to contractor"""
    
    contractor_email = maintenance_data['contractor_email']
    contractor_name = maintenance_data.get('contractor_name', 'Contractor')
    
    # Format priority display
    priority_colors = {
        'low': '#28a745',
        'medium': '#ffc107', 
        'high': '#fd7e14',
        'urgent': '#dc3545'
    }
    priority_color = priority_colors.get(maintenance_data['priority'], '#6c757d')
    
    # Format photos section
    photos_section = ""
    if maintenance_data.get('photos') and len(maintenance_data['photos']) > 0:
        photos_section = """
        <div style="margin: 20px 0;">
            <h4 style="color: #1a39ffff; margin-bottom: 10px;">📸 Photos:</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
        """
        for i, photo_base64 in enumerate(maintenance_data['photos']):
            photos_section += f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; width: 200px;">
                    <img src="{photo_base64}" alt="Issue Photo {i+1}" style="width: 100%; height: 150px; object-fit: cover;">
                    <p style="padding: 8px; margin: 0; font-size: 12px; background: #f8f9fa;">Photo {i+1}</p>
                </div>
            """
        photos_section += """
            </div>
        </div>
        """
    
    # Format additional message section
    additional_msg_section = ""
    if additional_message:
        additional_msg_section = f"""
        <div style="background-color: #e8f4ff; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #1a39ffff;">
            <h4 style="color: #1a39ffff; margin-top: 0;">💬 Additional Message from Admin:</h4>
            <p style="margin: 0; color: #333;">{additional_message}</p>
        </div>
        """
    
    # Format estimated cost
    cost_section = ""
    if maintenance_data.get('estimated_cost'):
        cost_section = f"""
        <p><strong>💰 Estimated Budget:</strong> <span style="color: #28a745; font-size: 16px;">${maintenance_data['estimated_cost']}</span></p>
        """
    
    subject = f"🔧 New Maintenance Request - {maintenance_data['issue_title']} | {COMPANY_NAME}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
        <div style="max-width: 800px; margin: auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #1a39ffff 0%, #4c6fff 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">🔧 New Maintenance Request</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Immediate attention required</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px;">
                <p style="font-size: 18px; color: #333; margin-bottom: 25px;">Hello {contractor_name},</p>
                <p style="color: #666; line-height: 1.6;">We have a new maintenance request that requires your expertise. Please review the details below and contact us to confirm availability.</p>
                
                <!-- Priority Badge -->
                <div style="margin: 25px 0;">
                    <span style="background-color: {priority_color}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; text-transform: uppercase; font-size: 12px;">
                        {maintenance_data['priority']} Priority
                    </span>
                </div>
                
                <!-- Property & Tenant Info -->
                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #1a39ffff; margin-top: 0; margin-bottom: 15px;">🏠 Property & Tenant Information</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <p style="margin: 5px 0;"><strong>📍 Address:</strong><br/>{maintenance_data['property_address']}</p>
                            {f"<p style='margin: 5px 0;'><strong>🚪 Unit:</strong> {maintenance_data['property_unit']}</p>" if maintenance_data.get('property_unit') else ""}
                        </div>
                        <div>
                            <p style="margin: 5px 0;"><strong>👤 Tenant:</strong> {maintenance_data['tenant_name']}</p>
                            {f"<p style='margin: 5px 0;'><strong>📞 Phone:</strong> {maintenance_data['tenant_phone']}</p>" if maintenance_data.get('tenant_phone') else ""}
                            {f"<p style='margin: 5px 0;'><strong>✉️ Email:</strong> {maintenance_data['tenant_email']}</p>" if maintenance_data.get('tenant_email') else ""}
                        </div>
                    </div>
                </div>
                
                <!-- Issue Details -->
                <div style="background-color: #ffffff; border: 2px solid #1a39ffff; border-radius: 10px; padding: 25px; margin: 25px 0;">
                    <h3 style="color: #1a39ffff; margin-top: 0; margin-bottom: 15px;">🔍 Issue Details</h3>
                    <h4 style="color: #333; margin: 10px 0;">{maintenance_data['issue_title']}</h4>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #1a39ffff;">
                        <p style="margin: 0; line-height: 1.6; color: #333;">{maintenance_data['issue_description']}</p>
                    </div>
                    {cost_section}
                    {f"<p><strong>📝 Additional Notes:</strong> {maintenance_data['notes']}</p>" if maintenance_data.get('notes') else ""}
                </div>
                
                {additional_msg_section}
                {photos_section}
                
                <!-- Contact Info -->
                <div style="background-color: #e8f4ff; padding: 20px; border-radius: 10px; margin: 25px 0;">
                    <h4 style="color: #1a39ffff; margin-top: 0;">📞 Next Steps</h4>
                    <ul style="color: #333; line-height: 1.8; padding-left: 20px;">
                        <li>Review the maintenance request details above</li>
                        <li>Contact our office to confirm availability and schedule</li>
                        <li>Coordinate directly with the tenant if needed</li>
                        <li>Provide a quote if requested</li>
                    </ul>
                    <p style="margin: 15px 0 5px 0;"><strong>Contact us:</strong></p>
                    <p style="margin: 5px 0;">📧 Email: <a href="mailto:{ADMIN_EMAIL}" style="color: #1a39ffff;">{ADMIN_EMAIL}</a></p>
                    <p style="margin: 5px 0;">🌐 Portal: <a href="{FRONTEND_URL}" style="color: #1a39ffff;">{FRONTEND_URL}</a></p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px; margin: 5px 0;">
                        This request was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
                    </p>
                    <p style="color: #666; font-size: 14px; margin: 5px 0;">
                        <strong>{COMPANY_NAME}</strong> | Professional Property Management
                    </p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return await send_email(contractor_email, subject, html_content)


async def send_maintenance_request_confirmation_to_admin(maintenance_data: dict, admin_email: str):
    """Send confirmation to admin that maintenance request was sent to contractor"""
    
    subject = f"✅ Maintenance Request Sent - {maintenance_data['issue_title']}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #28a745; margin: 0;">✅ Maintenance Request Sent Successfully</h2>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #1a39ffff; margin-top: 0;">Request Summary</h3>
                <p><strong>Issue:</strong> {maintenance_data['issue_title']}</p>
                <p><strong>Property:</strong> {maintenance_data['property_address']}</p>
                <p><strong>Tenant:</strong> {maintenance_data['tenant_name']}</p>
                <p><strong>Contractor:</strong> {maintenance_data['contractor_name'] or maintenance_data['contractor_email']}</p>
                <p><strong>Priority:</strong> <span style="text-transform: uppercase; color: #dc3545;">{maintenance_data['priority']}</span></p>
                <p><strong>Sent at:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            </div>
            
            <p style="color: #666; line-height: 1.6;">
                The maintenance request has been successfully sent to the contractor. 
                They should receive the email shortly with all the necessary details.
            </p>
            
            <div style="text-align: center; margin-top: 25px;">
                <p style="color: #666; font-size: 14px;">
                    {COMPANY_NAME} - Admin Notification System
                </p>
            </div>
        </div>
    </div>
    """
    
    return await send_email(admin_email, subject, html_content)