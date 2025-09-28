from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction
from typing import List, Optional
from datetime import date, datetime

from model.screeningQuestionModel import ScreeningQuestion, ScreeningResponse, ScreeningAnswer, QuestionType
from schemas.screeningQuestionSchemas import (
    CreateScreeningQuestion, UpdateScreeningQuestion, ScreeningQuestionResponse,
    CreateScreeningResponse, ScreeningResponseDetail, ScreeningResponseSummary,
    ScreeningAnswerResponse, PublicScreeningQuestion, ReorderQuestions
)

class ScreeningQuestionController:
    
    # ============ ADMIN QUESTION MANAGEMENT ============
    
    @staticmethod
    async def create_question(question_data: CreateScreeningQuestion) -> ScreeningQuestionResponse:
        """Create a new screening question (Admin only)"""
        try:
            # Check if order already exists and adjust if needed
            if question_data.order > 0:
                existing_question = await ScreeningQuestion.filter(order=question_data.order).first()
                if existing_question:
                    # Shift existing questions down
                    await ScreeningQuestion.filter(order__gte=question_data.order).update(
                        order=ScreeningQuestion.order + 1
                    )
            
            question = await ScreeningQuestion.create(
                question_text=question_data.question_text,
                question_type=question_data.question_type,
                is_required=question_data.is_required,
                order=question_data.order,
                placeholder_text=question_data.placeholder_text,
                is_active=question_data.is_active
            )
            
            return ScreeningQuestionResponse(
                id=str(question.id),
                question_text=question.question_text,
                question_type=question.question_type,
                is_required=question.is_required,
                order=question.order,
                placeholder_text=question.placeholder_text,
                is_active=question.is_active,
                created_at=question.created_at.isoformat(),
                updated_at=question.updated_at.isoformat()
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create question: {str(e)}")
    
    @staticmethod
    async def get_all_questions(include_inactive: bool = False) -> List[ScreeningQuestionResponse]:
        """Get all screening questions (Admin view)"""
        try:
            query = ScreeningQuestion.all().order_by('order', 'created_at')
            if not include_inactive:
                query = query.filter(is_active=True)
            
            questions = await query
            
            return [
                ScreeningQuestionResponse(
                    id=str(q.id),
                    question_text=q.question_text,
                    question_type=q.question_type,
                    is_required=q.is_required,
                    order=q.order,
                    placeholder_text=q.placeholder_text,
                    is_active=q.is_active,
                    created_at=q.created_at.isoformat(),
                    updated_at=q.updated_at.isoformat()
                ) for q in questions
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve questions: {str(e)}")
    
    @staticmethod
    async def update_question(question_id: str, question_data: UpdateScreeningQuestion) -> ScreeningQuestionResponse:
        """Update a screening question (Admin only)"""
        try:
            question = await ScreeningQuestion.get(id=question_id)
            
            # Handle order changes
            if question_data.order is not None and question_data.order != question.order:
                # Reorder other questions
                if question_data.order > question.order:
                    await ScreeningQuestion.filter(
                        order__gt=question.order,
                        order__lte=question_data.order
                    ).update(order=ScreeningQuestion.order - 1)
                else:
                    await ScreeningQuestion.filter(
                        order__gte=question_data.order,
                        order__lt=question.order
                    ).update(order=ScreeningQuestion.order + 1)
            
            # Update the question
            update_data = {k: v for k, v in question_data.dict().items() if v is not None}
            await question.update_from_dict(update_data)
            await question.save()
            
            return ScreeningQuestionResponse(
                id=str(question.id),
                question_text=question.question_text,
                question_type=question.question_type,
                is_required=question.is_required,
                order=question.order,
                placeholder_text=question.placeholder_text,
                is_active=question.is_active,
                created_at=question.created_at.isoformat(),
                updated_at=question.updated_at.isoformat()
            )
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Question not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update question: {str(e)}")
    
    @staticmethod
    async def delete_question(question_id: str) -> dict:
        """Delete a screening question (Admin only)"""
        try:
            question = await ScreeningQuestion.get(id=question_id)
            question_order = question.order
            
            # Delete the question
            await question.delete()
            
            # Reorder remaining questions
            await ScreeningQuestion.filter(order__gt=question_order).update(
                order=ScreeningQuestion.order - 1
            )
            
            return {"message": "Question deleted successfully"}
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Question not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete question: {str(e)}")
    
    @staticmethod
    async def reorder_questions(reorder_data: ReorderQuestions) -> dict:
        """Bulk reorder questions (Admin only)"""
        try:
            async with in_transaction():
                for item in reorder_data.question_orders:
                    question_id = item.get("question_id")
                    new_order = item.get("order")
                    
                    if question_id and new_order is not None:
                        await ScreeningQuestion.filter(id=question_id).update(order=new_order)
            
            return {"message": "Questions reordered successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to reorder questions: {str(e)}")
    
    # ============ PUBLIC QUESTION ACCESS ============
    
    @staticmethod
    async def get_active_questions() -> List[PublicScreeningQuestion]:
        """Get active screening questions for users to fill out"""
        try:
            questions = await ScreeningQuestion.filter(is_active=True).order_by('order', 'created_at')
            
            return [
                PublicScreeningQuestion(
                    id=str(q.id),
                    question_text=q.question_text,
                    question_type=q.question_type,
                    is_required=q.is_required,
                    order=q.order,
                    placeholder_text=q.placeholder_text
                ) for q in questions
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve questions: {str(e)}")
    
    # ============ USER RESPONSE MANAGEMENT ============
    
    @staticmethod
    async def submit_response(response_data: CreateScreeningResponse) -> dict:
        """Submit screening response (Public)"""
        try:
            async with in_transaction():
                # Create the main response
                response = await ScreeningResponse.create(
                    full_name=response_data.full_name,
                    email=response_data.email,
                    message=response_data.message
                )
                
                # Validate and create answers
                for answer_data in response_data.answers:
                    # Check if question exists and is active
                    try:
                        question = await ScreeningQuestion.get(
                            id=answer_data.question_id,
                            is_active=True
                        )
                    except DoesNotExist:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Question {answer_data.question_id} not found or inactive"
                        )
                    
                    # Validate answer based on question type
                    answer_value = None
                    if question.question_type == QuestionType.TEXT:
                        if not answer_data.answer_text:
                            if question.is_required:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Text answer required for question: {question.question_text}"
                                )
                        else:
                            answer_value = answer_data.answer_text
                    
                    elif question.question_type == QuestionType.NUMBER:
                        if answer_data.answer_number is None:
                            if question.is_required:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Number answer required for question: {question.question_text}"
                                )
                        else:
                            answer_value = answer_data.answer_number
                    
                    elif question.question_type == QuestionType.DATE:
                        if not answer_data.answer_date:
                            if question.is_required:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Date answer required for question: {question.question_text}"
                                )
                        else:
                            answer_value = answer_data.answer_date
                    
                    # Create the answer
                    await ScreeningAnswer.create(
                        response=response,
                        question=question,
                        answer_text=answer_data.answer_text,
                        answer_number=answer_data.answer_number,
                        answer_date=answer_data.answer_date
                    )
                
                return {
                    "message": "Screening response submitted successfully",
                    "response_id": str(response.id)
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to submit response: {str(e)}")
    
    # ============ ADMIN RESPONSE MANAGEMENT ============
    
    @staticmethod
    async def get_all_responses(
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> dict:
        """Get all screening responses (Admin only)"""
        try:
            query = ScreeningResponse.all()
            
            # Apply search filter
            if search:
                query = query.filter(
                    full_name__icontains=search
                ) | query.filter(
                    email__icontains=search
                )
            
            # Get total count
            total = await query.count()
            
            # Apply pagination
            responses = await query.order_by('-created_at').offset(offset).limit(limit)
            
            # Get answer counts for each response
            response_list = []
            for response in responses:
                answer_count = await ScreeningAnswer.filter(response=response).count()
                response_list.append(
                    ScreeningResponseSummary(
                        id=str(response.id),
                        full_name=response.full_name,
                        email=response.email,
                        answers_count=answer_count,
                        created_at=response.created_at.isoformat()
                    )
                )
            
            return {
                "responses": response_list,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total,
                    "has_prev": offset > 0
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve responses: {str(e)}")
    
    @staticmethod
    async def get_response_detail(response_id: str) -> ScreeningResponseDetail:
        """Get detailed screening response with answers (Admin only)"""
        try:
            response = await ScreeningResponse.get(id=response_id)
            
            # Get all answers with question details
            answers = await ScreeningAnswer.filter(response=response).prefetch_related('question')
            
            answer_list = []
            for answer in answers:
                # Determine the answer value based on question type
                answer_value = None
                if answer.question.question_type == QuestionType.TEXT:
                    answer_value = answer.answer_text
                elif answer.question.question_type == QuestionType.NUMBER:
                    answer_value = answer.answer_number
                elif answer.question.question_type == QuestionType.DATE:
                    answer_value = answer.answer_date
                
                answer_list.append(
                    ScreeningAnswerResponse(
                        id=str(answer.id),
                        question_id=str(answer.question.id),
                        question_text=answer.question.question_text,
                        question_type=answer.question.question_type,
                        answer_text=answer.answer_text,
                        answer_number=answer.answer_number,
                        answer_date=answer.answer_date,
                        answer_value=answer_value,
                        created_at=answer.created_at.isoformat()
                    )
                )
            
            return ScreeningResponseDetail(
                id=str(response.id),
                full_name=response.full_name,
                email=response.email,
                message=response.message,
                answers=answer_list,
                created_at=response.created_at.isoformat(),
                updated_at=response.updated_at.isoformat()
            )
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Response not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve response: {str(e)}")
    
    @staticmethod
    async def delete_response(response_id: str) -> dict:
        """Delete a screening response (Admin only)"""
        try:
            response = await ScreeningResponse.get(id=response_id)
            await response.delete()
            
            return {"message": "Response deleted successfully"}
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Response not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete response: {str(e)}")