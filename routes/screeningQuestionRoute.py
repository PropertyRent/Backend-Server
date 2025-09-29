from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from controller.screeningQuestionController import ScreeningQuestionController
from schemas.screeningQuestionSchemas import (
    CreateScreeningQuestion, UpdateScreeningQuestion, ScreeningQuestionResponse,
    CreateScreeningResponse, ScreeningResponseDetail, ScreeningResponseSummary,
    PublicScreeningQuestion, ReorderQuestions
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter()

# ============ ADMIN ROUTES - Question Management ============

@router.post("/admin/screening/questions", response_model=ScreeningQuestionResponse)
async def create_screening_question(
    question_data: CreateScreeningQuestion,
    current_user=Depends(require_admin)
):
    """
    Create a new screening question (Admin only)
    
    - **question_text**: The question text (5-500 characters)
    - **question_type**: Type of question (text, number, date)
    - **is_required**: Whether the question is required (default: true)
    - **order**: Order of the question (default: 0)
    - **placeholder_text**: Placeholder text for input field
    - **is_active**: Whether the question is active (default: true)
    """
    return await ScreeningQuestionController.create_question(question_data)

@router.get("/admin/screening/questions", response_model=List[ScreeningQuestionResponse])
async def get_all_screening_questions(
    include_inactive: bool = Query(False, description="Include inactive questions"),
    current_user=Depends(require_admin)
):
    """
    Get all screening questions (Admin only)
    
    - **include_inactive**: Include inactive questions in results
    """
    return await ScreeningQuestionController.get_all_questions(include_inactive)

@router.put("/admin/screening/questions/{question_id}", response_model=ScreeningQuestionResponse)
async def update_screening_question(
    question_id: str,
    question_data: UpdateScreeningQuestion,
    current_user=Depends(require_admin)
):
    """
    Update a screening question (Admin only)
    
    - **question_id**: UUID of the question to update
    - Only provided fields will be updated
    """
    return await ScreeningQuestionController.update_question(question_id, question_data)

@router.delete("/admin/screening/questions/{question_id}")
async def delete_screening_question(
    question_id: str,
    current_user=Depends(require_admin)
):
    """
    Delete a screening question (Admin only)
    
    - **question_id**: UUID of the question to delete
    - This will also delete all associated answers
    """
    return await ScreeningQuestionController.delete_question(question_id)

@router.put("/admin/screening/questions/reorder")
async def reorder_screening_questions(
    reorder_data: ReorderQuestions,
    current_user=Depends(require_admin)
):
    """
    Bulk reorder screening questions (Admin only)
    
    - **question_orders**: List of {question_id, order} objects
    """
    return await ScreeningQuestionController.reorder_questions(reorder_data)

# ============ ADMIN ROUTES - Response Management ============

@router.get("/admin/screening/responses")
async def get_all_screening_responses(
    limit: int = Query(20, ge=1, le=100, description="Number of responses to return"),
    offset: int = Query(0, ge=0, description="Number of responses to skip"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user=Depends(require_admin)
):
    """
    Get all screening responses (Admin only)
    
    - **limit**: Number of responses to return (1-100)
    - **offset**: Number of responses to skip for pagination
    - **search**: Search by full name or email
    """
    return await ScreeningQuestionController.get_all_responses(limit, offset, search)

@router.get("/admin/screening/responses/{response_id}", response_model=ScreeningResponseDetail)
async def get_screening_response_detail(
    response_id: str,
    current_user=Depends(require_admin)
):
    """
    Get detailed screening response with all answers (Admin only)
    
    - **response_id**: UUID of the response to retrieve
    """
    return await ScreeningQuestionController.get_response_detail(response_id)

@router.delete("/admin/screening/responses/{response_id}")
async def delete_screening_response(
    response_id: str,
    current_user=Depends(require_admin)
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
    - **message**: Optional message from the applicant
    - **answers**: List of answers to the screening questions
    
    Each answer should include:
    - **question_id**: UUID of the question being answered
    - **answer_text**: For text questions
    - **answer_number**: For number questions
    - **answer_date**: For date questions (YYYY-MM-DD format)
    """
    return await ScreeningQuestionController.submit_response(response_data)