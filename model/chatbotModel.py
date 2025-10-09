import uuid
from enum import Enum
from tortoise import fields, models
from datetime import datetime


class ChatbotFlowType(str, Enum):
    PROPERTY_SEARCH = "property_search"
    RENT_INQUIRY = "rent_inquiry" 
    SCHEDULE_VISIT = "schedule_visit"
    GENERAL_SUPPORT = "general_support"
    BUG_REPORT = "bug_report"
    FEEDBACK = "feedback"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class ChatbotConversation(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    session_id = fields.CharField(max_length=255, unique=True, index=True)  # Frontend session ID
    flow_type = fields.CharEnumField(ChatbotFlowType, null=True)
    
    # User info (if available)
    user = fields.ForeignKeyField("models.User", related_name="chatbot_conversations", null=True, on_delete=fields.SET_NULL)
    guest_email = fields.CharField(max_length=255, null=True)  # For guest users
    guest_name = fields.CharField(max_length=255, null=True)
    
    # Conversation state
    current_step = fields.IntField(default=0)
    status = fields.CharEnumField(ConversationStatus, default=ConversationStatus.ACTIVE)
    
    # Final satisfaction
    is_satisfied = fields.BooleanField(null=True)  # null = not asked yet, True/False = answered
    
    # Metadata
    user_ip = fields.CharField(max_length=45, null=True)
    user_agent = fields.TextField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "chatbot_conversations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conversation {self.session_id} - {self.flow_type}"


class ChatbotMessage(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    conversation = fields.ForeignKeyField("models.ChatbotConversation", related_name="messages", on_delete=fields.CASCADE)
    
    # Message details
    step_number = fields.IntField()  # Question number in flow
    question_text = fields.TextField()  # Bot's question
    user_response = fields.TextField(null=True)  # User's answer
    
    # Metadata
    response_time_seconds = fields.IntField(null=True)  # How long user took to respond
    
    created_at = fields.DatetimeField(auto_now_add=True)
    responded_at = fields.DatetimeField(null=True)

    class Meta:
        table = "chatbot_messages"
        ordering = ["step_number"]

    def __str__(self):
        return f"Step {self.step_number}: {self.question_text[:50]}..."


class ChatbotEscalation(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    conversation = fields.ForeignKeyField("models.ChatbotConversation", related_name="escalations", on_delete=fields.CASCADE)
    
    # Escalation details
    reason = fields.CharField(max_length=100)  # "unsatisfied", "complex_query", "technical_issue"
    priority = fields.CharField(max_length=20, default="medium")  # low, medium, high, urgent
    
    # Admin handling
    assigned_to = fields.ForeignKeyField("models.User", related_name="assigned_escalations", null=True, on_delete=fields.SET_NULL)
    status = fields.CharField(max_length=50, default="pending")  # pending, in_progress, resolved, closed
    admin_notes = fields.TextField(null=True)
    
    # Contact info
    contact_email = fields.CharField(max_length=255)
    contact_name = fields.CharField(max_length=255, null=True)
    contact_phone = fields.CharField(max_length=20, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    resolved_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "chatbot_escalations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Escalation: {self.reason} - {self.status}"