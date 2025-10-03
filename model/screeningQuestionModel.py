from tortoise.models import Model
from tortoise import fields
import uuid
from enum import Enum

class QuestionType(str, Enum):
    TEXT = "text"
    NUMBER = "number" 
    DATE = "date"
    YESNO = "yesno"

class ScreeningQuestion(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    question_text = fields.TextField()
    question_type = fields.CharEnumField(QuestionType, max_length=10)
    is_required = fields.BooleanField(default=True)
    order = fields.IntField(default=0)  # For ordering questions
    placeholder_text = fields.CharField(max_length=255, null=True)  # Placeholder for input fields
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "screening_questions"
        ordering = ["order", "created_at"]

class ScreeningResponse(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    full_name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=150)
    phone = fields.CharField(max_length=20)  # Added phone field for user contact
    message = fields.TextField(null=True)  # Optional message from user
    admin_reply = fields.TextField(null=True)  # Admin's reply to the response
    replied_at = fields.DatetimeField(null=True)  # When admin replied
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "screening_responses"

class ScreeningAnswer(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    response = fields.ForeignKeyField("models.ScreeningResponse", related_name="answers", on_delete=fields.CASCADE)
    question = fields.ForeignKeyField("models.ScreeningQuestion", related_name="answers", on_delete=fields.CASCADE)
    answer_text = fields.TextField(null=True)  # For text answers
    answer_number = fields.IntField(null=True)  # For number answers
    answer_date = fields.DateField(null=True)  # For date answers
    answer_yesno = fields.BooleanField(null=True)  # For yes/no answers
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "screening_answers"
        unique_together = (("response", "question"),)  # One answer per question per response