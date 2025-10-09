import uuid
from tortoise import fields, models


class Property(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)

    property_type = fields.CharField(max_length=100, null=False)  
    status = fields.CharField(max_length=50, null=False)  
    furnishing = fields.CharField(max_length=100, null=True)

    area_sqft = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    bedrooms = fields.IntField(null=True)
    bathrooms = fields.IntField(null=True)
    floors = fields.IntField(null=True)

    utilities = fields.JSONField(null=True)   
    lease_term = fields.TextField(null=True)
    application_fee = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    amenities = fields.JSONField(null=True)   
    pet_policy = fields.TextField(null=True)

    
    appliances_included = fields.JSONField(null=True)  

    property_management_contact = fields.TextField(null=True)
    website = fields.CharField(max_length=255, null=True)

    price = fields.DecimalField(max_digits=12, decimal_places=2, null=False)
    deposit = fields.DecimalField(max_digits=12, decimal_places=2, null=True)

    address = fields.TextField(null=True)
    city = fields.CharField(max_length=100, null=True)
    state = fields.CharField(max_length=100, null=True)
    pincode = fields.CharField(max_length=20, null=True)

    latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)

    available_from = fields.DatetimeField(auto_now_add=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "properties"

    def __str__(self):
        return self.title
