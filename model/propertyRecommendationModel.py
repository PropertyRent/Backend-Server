import uuid
from tortoise import fields, models
from model.propertyModel import Property
from model.screeningQuestionModel import ScreeningQuestion


class PropertyRecommendation(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # User information (from screening)
    user_email = fields.CharField(max_length=255, null=False, index=True)
    user_name = fields.CharField(max_length=255, null=True)
    user_phone = fields.CharField(max_length=20, null=True)
    
    # Screening criteria
    screening_id = fields.UUIDField(null=True)  # Reference to screening submission
    budget_min = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    budget_max = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    preferred_location = fields.CharField(max_length=255, null=True)
    bedrooms_required = fields.IntField(null=True)
    bathrooms_required = fields.IntField(null=True)
    property_type_preference = fields.CharField(max_length=100, null=True)
    move_in_date = fields.DateField(null=True)
    
    # Recommendation data
    recommended_properties = fields.JSONField(default=list)  # List of property IDs and match scores
    match_score = fields.FloatField(default=0.0)  # Overall match score (0-100)
    match_criteria = fields.JSONField(default=dict)  # What criteria matched
    
    # Status tracking
    status = fields.CharField(max_length=50, default="pending")  # pending, sent, viewed, interested, rejected
    email_sent = fields.BooleanField(default=False)
    email_sent_at = fields.DatetimeField(null=True)
    user_response = fields.CharField(max_length=50, null=True)  # interested, not_interested, need_more_info
    user_responded_at = fields.DatetimeField(null=True)
    
    # Admin tracking
    admin_reviewed = fields.BooleanField(default=False)
    admin_notes = fields.TextField(null=True)
    priority_level = fields.CharField(max_length=20, default="normal")  # high, normal, low
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "property_recommendations"