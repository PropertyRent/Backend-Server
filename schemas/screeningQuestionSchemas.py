from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union, Any
from datetime import date
from enum import Enum

class QuestionType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    YESNO = "yesno"

# Schema for creating a new screening question (Admin only)
class CreateScreeningQuestion(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=500, description="The question text")
    question_type: QuestionType = Field(..., description="Type of question: text, number, date, or yesno")
    is_required: bool = Field(default=True, description="Whether this question is required")
    order: int = Field(default=0, ge=0, description="Order of the question (0 = first)")
    placeholder_text: Optional[str] = Field(None, max_length=255, description="Placeholder text for the input field")
    is_active: bool = Field(default=True, description="Whether this question is active")

# Schema for updating a screening question (Admin only)
class UpdateScreeningQuestion(BaseModel):
    question_text: Optional[str] = Field(None, min_length=5, max_length=500)
    question_type: Optional[QuestionType] = None
    is_required: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)
    placeholder_text: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

# Schema for screening question response (Read)
class ScreeningQuestionResponse(BaseModel):
    id: str
    question_text: str
    question_type: QuestionType
    is_required: bool
    order: int
    placeholder_text: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Schema for individual answer
class ScreeningAnswerInput(BaseModel):
    question_id: str = Field(..., description="UUID of the question being answered")
    answer_text: Optional[str] = Field(None, max_length=1000, description="Text answer for text questions")
    answer_number: Optional[int] = Field(None, ge=0, description="Number answer for number questions") 
    answer_date: Optional[date] = Field(None, description="Date answer for date questions")
    answer_yesno: Optional[bool] = Field(None, description="Boolean answer for yes/no questions")

    def get_answer_value(self) -> Union[str, int, date, bool, None]:
        """Get the actual answer value based on what's provided"""
        if self.answer_text is not None:
            return self.answer_text
        elif self.answer_number is not None:
            return self.answer_number
        elif self.answer_date is not None:
            return self.answer_date
        elif self.answer_yesno is not None:
            return self.answer_yesno
        return None

# Schema for creating a screening response (User submission)
class CreateScreeningResponse(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the applicant")
    email: EmailStr = Field(..., description="Email address of the applicant")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number of the applicant")
    message: Optional[str] = Field(None, max_length=1000, description="Optional message from the applicant")
    answers: List[ScreeningAnswerInput] = Field(..., min_items=1, description="List of answers to the screening questions")

# Schema for screening answer response (Read)
class ScreeningAnswerResponse(BaseModel):
    id: str
    question_id: str
    question_text: str
    question_type: QuestionType
    answer_text: Optional[str]
    answer_number: Optional[int]
    answer_date: Optional[date]
    answer_yesno: Optional[bool]
    answer_value: Optional[Union[str, int, date, bool]]  # Computed field for the actual answer
    created_at: str

    class Config:
        from_attributes = True

# Schema for screening response (Read)
class ScreeningResponseDetail(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    message: Optional[str]
    admin_reply: Optional[str]
    replied_at: Optional[str]
    answers: List[ScreeningAnswerResponse]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Schema for screening response list (Admin view)
class ScreeningResponseSummary(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    answers_count: int
    has_admin_reply: bool
    created_at: str

    class Config:
        from_attributes = True

# Schema for bulk question creation (Admin only)
class BulkCreateScreeningQuestions(BaseModel):
    questions: List[CreateScreeningQuestion] = Field(..., min_items=1, max_items=20, description="List of questions to create (max 20)")
    
    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    {
                        "question_text": "What is your preferred monthly rent budget?",
                        "question_type": "text",
                        "is_required": True,
                        "order": 1,
                        "placeholder_text": "e.g., $2000-$2500"
                    },
                    {
                        "question_text": "How many bedrooms do you need?",
                        "question_type": "number",
                        "is_required": True,
                        "order": 2,
                        "placeholder_text": "Enter number of bedrooms"
                    },
                    {
                        "question_text": "When would you like to move in?",
                        "question_type": "date",
                        "is_required": True,
                        "order": 3,
                        "placeholder_text": "Select your preferred move-in date"
                    },
                    {
                        "question_text": "Do you have any pets?",
                        "question_type": "yesno",
                        "is_required": True,
                        "order": 4,
                        "placeholder_text": "Select Yes or No"
                    }
                ]
            }
        }

# Schema for bulk question creation response
class BulkCreateResponse(BaseModel):
    success: bool
    message: str
    created_questions: List[ScreeningQuestionResponse]
    failed_questions: List[dict] = []

# Schema for bulk question reordering
class ReorderQuestions(BaseModel):
    question_orders: List[dict] = Field(..., description="List of {question_id: str, order: int}")

# Schema for getting all active questions (Public view)
class PublicScreeningQuestion(BaseModel):
    id: str
    question_text: str
    question_type: QuestionType
    is_required: bool
    order: int
    placeholder_text: Optional[str]

    class Config:
        from_attributes = True