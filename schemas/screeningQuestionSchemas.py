from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union, Any
from datetime import date
from enum import Enum

class QuestionType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"

# Schema for creating a new screening question (Admin only)
class CreateScreeningQuestion(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=500, description="The question text")
    question_type: QuestionType = Field(..., description="Type of question: text, number, or date")
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

    def get_answer_value(self) -> Union[str, int, date, None]:
        """Get the actual answer value based on what's provided"""
        if self.answer_text is not None:
            return self.answer_text
        elif self.answer_number is not None:
            return self.answer_number
        elif self.answer_date is not None:
            return self.answer_date
        return None

# Schema for creating a screening response (User submission)
class CreateScreeningResponse(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the applicant")
    email: EmailStr = Field(..., description="Email address of the applicant")
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
    answer_value: Optional[Union[str, int, date]]  # Computed field for the actual answer
    created_at: str

    class Config:
        from_attributes = True

# Schema for screening response (Read)
class ScreeningResponseDetail(BaseModel):
    id: str
    full_name: str
    email: str
    message: Optional[str]
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
    answers_count: int
    created_at: str

    class Config:
        from_attributes = True

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