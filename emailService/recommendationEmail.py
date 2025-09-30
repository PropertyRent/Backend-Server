import os
from typing import List, Dict
from config.nodemailer import send_email


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "no-reply@example.com")


async def send_property_recommendations_email(
    to_email: str, 
    user_name: str, 
    recommendations: List[Dict], 
    match_score: float,
    recommendation_id: str
):
    """Send property recommendations email to user"""
    
    # Create property cards HTML
    property_cards = ""
    for i, prop in enumerate(recommendations[:5]):  # Show top 5 properties
        property_cards += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: #fff;">
            <h3 style="color: #1a39ff; margin: 0 0 10px 0;">{prop.get('title', 'Property')}</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span><strong>Price:</strong> ${prop.get('price', 'N/A'):,.2f}/month</span>
                <span><strong>Match Score:</strong> {prop.get('match_score', 0):.1f}%</span>
            </div>
            <div style="margin-bottom: 10px;">
                <strong>Location:</strong> {prop.get('location', 'Location TBD')}<br/>
                <strong>Type:</strong> {prop.get('property_type', 'N/A')} | 
                <strong>Bedrooms:</strong> {prop.get('bedrooms', 'N/A')} | 
                <strong>Bathrooms:</strong> {prop.get('bathrooms', 'N/A')}
            </div>
            {f'<p style="color: #666; font-size: 14px;">{prop.get("description", "")}</p>' if prop.get('description') else ''}
            <div style="margin-top: 10px;">
                <strong>Why this matches:</strong>
                <ul style="color: #666; font-size: 14px; margin: 5px 0;">
                    {' '.join([f'<li>{reason}</li>' for reason in prop.get('match_reasons', [])])}
                </ul>
            </div>
        </div>
        """
    
    subject = f"🏠 {len(recommendations)} Property Recommendations Just for You!"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f5f7fa; padding: 30px;">
      <div style="max-width: 700px; margin: auto; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1a39ff, #4f46e5); color: white; padding: 30px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">🏠 Your Perfect Property Matches!</h1>
          <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Based on your screening questionnaire</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
          <p style="font-size: 16px; color: #333;">Hi {user_name or 'there'},</p>
          
          <p style="font-size: 16px; color: #333; line-height: 1.6;">
            Great news! Based on your screening questionnaire responses, we've found <strong>{len(recommendations)} properties</strong> 
            that match your requirements with an overall match score of <strong>{match_score:.1f}%</strong>.
          </p>
          
          <div style="background: #e3f2fd; border-left: 4px solid #1a39ff; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; color: #1565c0; font-weight: bold;">✨ These properties were specifically selected based on:</p>
            <ul style="color: #1565c0; margin: 10px 0 0 20px;">
              <li>Your budget preferences</li>
              <li>Preferred location</li>
              <li>Bedroom and bathroom requirements</li>
              <li>Property type preferences</li>
            </ul>
          </div>
          
          <h2 style="color: #1a39ff; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">🎯 Your Recommended Properties</h2>
          
          {property_cards}
          
          {f'<p style="text-align: center; color: #666; font-style: italic; margin: 20px 0;">Showing top 5 properties. <a href="{FRONTEND_URL}/recommendations/{recommendation_id}" style="color: #1a39ff;">View all {len(recommendations)} recommendations</a></p>' if len(recommendations) > 5 else ''}
          
          <!-- Call to Action -->
          <div style="background: #f8f9fa; border-radius: 8px; padding: 25px; margin: 30px 0; text-align: center;">
            <h3 style="color: #1a39ff; margin: 0 0 15px 0;">Interested in any of these properties?</h3>
            <div style="margin: 20px 0;">
              <a href="{FRONTEND_URL}/recommendations/{recommendation_id}/respond?response=interested" 
                 style="background: #1a39ff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block; font-weight: bold;">
                😍 I'm Interested!
              </a>
              <a href="{FRONTEND_URL}/recommendations/{recommendation_id}/respond?response=need_more_info" 
                 style="background: #6c757d; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block; font-weight: bold;">
                🤔 Need More Info
              </a>
            </div>
            <p style="color: #666; font-size: 14px; margin: 15px 0 0 0;">
              Click the buttons above to let us know your interest level, or 
              <a href="{FRONTEND_URL}/contact" style="color: #1a39ff;">contact us directly</a> 
              to schedule a property viewing.
            </p>
          </div>
          
          <div style="border-top: 1px solid #e0e0e0; padding-top: 20px; margin-top: 30px; color: #666; font-size: 14px;">
            <p><strong>Need help?</strong> Our property experts are here to assist you every step of the way.</p>
            <p>📧 Reply to this email | 🌐 <a href="{FRONTEND_URL}" style="color: #1a39ff;">Visit our website</a></p>
          </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px;">
          <p style="margin: 0;">This email was sent because you completed our property screening questionnaire.</p>
          <p style="margin: 5px 0 0 0;">© 2025 Property-Rent. All rights reserved.</p>
        </div>
        
      </div>
    </div>
    """
    
    return await send_email(to_email, subject, html_content)


async def send_recommendation_notification_to_admin(
    user_email: str,
    user_name: str,
    property_count: int,
    match_score: float,
    recommendation_id: str
):
    """Send notification to admin when new recommendations are generated"""
    subject = f"🎯 New Property Recommendations Generated - {user_name or user_email}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ff;">🎯 New Property Recommendations Generated</h2>
        
        <div style="background: #e8f5e8; border-radius: 8px; padding: 15px; margin: 20px 0;">
          <h3 style="color: #2e7d32; margin: 0 0 10px 0;">User Information:</h3>
          <p style="margin: 5px 0;"><strong>Name:</strong> {user_name or 'Not provided'}</p>
          <p style="margin: 5px 0;"><strong>Email:</strong> {user_email}</p>
        </div>
        
        <div style="background: #fff3e0; border-radius: 8px; padding: 15px; margin: 20px 0;">
          <h3 style="color: #f57c00; margin: 0 0 10px 0;">Recommendation Summary:</h3>
          <p style="margin: 5px 0;"><strong>Properties Found:</strong> {property_count}</p>
          <p style="margin: 5px 0;"><strong>Match Score:</strong> {match_score:.1f}%</p>
          <p style="margin: 5px 0;"><strong>Status:</strong> Pending Review</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
          <a href="{FRONTEND_URL}/admin/recommendations/{recommendation_id}" 
             style="background: #1a39ff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
            Review Recommendations
          </a>
        </div>
        
        <p style="color: #666; font-size: 14px; margin-top: 20px;">
          The system has automatically matched this user with available properties. 
          Please review the recommendations and follow up if needed.
        </p>
        
        <p style="margin-top: 20px;">Best regards,<br/>Property-Rent Automation System</p>
      </div>
    </div>
    """
    return await send_email(ADMIN_EMAIL, subject, html_content)