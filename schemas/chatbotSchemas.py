from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


class StartChatRequest(BaseModel):
    session_id: Optional[str] = None  # If continuing existing chat
    user_agent: Optional[str] = None
    user_ip: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    user_response: str
    

class ChatbotResponse(BaseModel):
    session_id: str
    question: str
    step_number: int
    options: Optional[List[str]] = None  # For multiple choice questions
    input_type: str = "text"  # text, choice, email, phone, number, date
    is_final: bool = False  # Is this the last question?
    flow_type: Optional[str] = None
    

class SatisfactionResponse(BaseModel):
    session_id: str
    is_satisfied: bool
    feedback: Optional[str] = None


class ConversationSummary(BaseModel):
    id: str
    session_id: str
    flow_type: Optional[str]
    status: str
    is_satisfied: Optional[bool]
    user_name: Optional[str]
    user_email: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    messages_count: int
    

class MessageSummary(BaseModel):
    step_number: int
    question: str
    answer: Optional[str]
    response_time: Optional[int]


class EscalationRequest(BaseModel):
    session_id: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    reason: str = "unsatisfied"
    additional_notes: Optional[str] = None


class EscalationSummary(BaseModel):
    id: str
    conversation_id: str
    reason: str
    priority: str
    status: str
    contact_name: str
    contact_email: str
    created_at: datetime
    resolved_at: Optional[datetime] = None