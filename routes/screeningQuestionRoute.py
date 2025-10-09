from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from controller.screeningQuestionController import ScreeningQuestionController
from schemas.screeningQuestionSchemas import (
    CreateScreeningResponse, ScreeningResponseDetail,
    PublicScreeningQuestion, BulkCreateScreeningQuestions, BulkCreateResponse
)
from authMiddleware.roleMiddleware import require_admin

router = APIRouter()

# ============ ADMIN ROUTES - Question Management ============

@router.post("/admin/screening/questions/bulk", response_model=BulkCreateResponse)
async def bulk_create_screening_questions(
    questions_data: BulkCreateScreeningQuestions,
):
    """
    Create multiple screening questions at once (Admin only)
    
    - **questions**: List of 1-20 questions to create
    - Each question can be text, number, date, or yesno type
    - Questions are created in the order provided
    - If any question fails, the entire operation is rolled back
    
    **Example request body:**
    ```json
    {
        "questions": [
            {
                "question_text": "What is your full name?",
                "question_type": "text",
                "is_required": true,
                "placeholder": "Enter your full name"
            },
            {
                "question_text": "What is your monthly income?",
                "question_type": "number",
                "is_required": true,
                "placeholder": "Enter amount in USD"
            },
            {
                "question_text": "Do you have pets?",
                "question_type": "yesno",
                "is_required": true
            }
        ]
    }
    ```
    
    **Response includes:**
    - **total_requested**: Number of questions requested to create
    - **total_created**: Number of questions successfully created
    - **created_questions**: List of created question details
    - **errors**: List of any errors encountered (if partial success)
    """
    return await ScreeningQuestionController.bulk_create_questions(questions_data)

@router.delete("/admin/screening/questions/{question_id}")
async def delete_screening_question(
    question_id: str,
):
    """
    Delete a screening question (Admin only)
    
    - **question_id**: UUID of the question to delete
    - This will also delete all associated answers
    """
    return await ScreeningQuestionController.delete_question(question_id)

# ============ ADMIN ROUTES - Response Management ============

@router.get("/admin/screening/responses")
async def get_all_screening_responses(
    limit: int = Query(20, ge=1, le=100, description="Number of responses to return"),
    offset: int = Query(0, ge=0, description="Number of responses to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
):
    """
    Get all screening responses with user details (Admin only)
    
    - **limit**: Number of responses to return (1-100)
    - **offset**: Number of responses to skip for pagination
    - **search**: Search by full name or email
    """
    return await ScreeningQuestionController.get_all_responses(limit, offset, search)

@router.get("/admin/screening/responses/{response_id}", response_model=ScreeningResponseDetail)
async def get_screening_response_detail(
    response_id: str,
):
    """
    Get detailed screening response with all answers (Admin only)
    
    - **response_id**: UUID of the response to retrieve
    """
    return await ScreeningQuestionController.get_response_detail(response_id)

@router.put("/admin/screening/responses/{response_id}/reply")
async def reply_to_screening_response(
    response_id: str,
    reply_data: dict,
):
    """
    Reply to a screening response (Admin only)
    
    - **response_id**: UUID of the response to reply to
    - **reply_message**: Admin's reply message
    """
    return await ScreeningQuestionController.reply_to_response(response_id, reply_data.get("reply_message"))

@router.delete("/admin/screening/responses/{response_id}")
async def delete_screening_response(
    response_id: str,
):
    """
    Delete a screening response (Admin only)
    
    - **response_id**: UUID of the response to delete
    - This will also delete all associated answers
    """
    return await ScreeningQuestionController.delete_response(response_id)

# ============ PUBLIC ROUTES ============

@router.get("/public/screening/questions", response_model=List[PublicScreeningQuestion])
async def get_active_screening_questions():
    """
    Get active screening questions for users to fill out (Public access)
    
    Returns only active questions ordered by their sequence
    """
    return await ScreeningQuestionController.get_active_questions()

@router.post("/public/screening/responses")
async def submit_screening_response(response_data: CreateScreeningResponse):
    """
    Submit screening response (Public access)
    
    - **full_name**: Full name of the applicant (2-100 characters)
    - **email**: Valid email address
    - **phone**: Phone number of the applicant (10-20 characters)
    - **message**: Optional message from the applicant
    - **answers**: List of answers to the screening questions
    
    Each answer should include:
    - **question_id**: UUID of the question being answered
    - **answer_text**: For text questions
    - **answer_number**: For number questions
    - **answer_date**: For date questions (YYYY-MM-DD format)
    - **answer_yesno**: For yes/no questions (true/false)
    """
    return await ScreeningQuestionController.submit_response(response_data)