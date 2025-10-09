from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction
from typing import List, Optional
from datetime import date, datetime

from model.screeningQuestionModel import ScreeningQuestion, ScreeningResponse, ScreeningAnswer, QuestionType
from schemas.screeningQuestionSchemas import (
    CreateScreeningResponse, ScreeningResponseDetail, ScreeningResponseSummary,
    ScreeningAnswerResponse, PublicScreeningQuestion, 
    BulkCreateScreeningQuestions, BulkCreateResponse
)

class ScreeningQuestionController:
    
    # ============ ADMIN QUESTION MANAGEMENT ============
    
    @staticmethod
    async def bulk_create_questions(bulk_data: BulkCreateScreeningQuestions) -> BulkCreateResponse:
        """Create multiple screening questions at once (Admin only)"""
        created_questions = []
        failed_questions = []
        
        try:
            async with in_transaction():
                # Get the current highest order number
                max_order_question = await ScreeningQuestion.all().order_by('-order').first()
                next_order = (max_order_question.order + 1) if max_order_question else 1
                
                for i, question_data in enumerate(bulk_data.questions):
                    try:
                        # Determine the order for this question
                        if question_data.order > 0:
                            # Use the specified order
                            target_order = question_data.order
                            # Check if order already exists and adjust if needed
                            existing_question = await ScreeningQuestion.filter(order=target_order).first()
                            if existing_question:
                                # Shift existing questions down
                                questions_to_update = await ScreeningQuestion.filter(order__gte=target_order).all()
                                for q in questions_to_update:
                                    q.order += 1
                                    await q.save()
                        else:
                            # Auto-assign sequential order starting from next available
                            target_order = next_order + i
                        
                        question = await ScreeningQuestion.create(
                            question_text=question_data.question_text,
                            question_type=question_data.question_type,
                            is_required=question_data.is_required,
                            order=target_order,
                            placeholder_text=question_data.placeholder_text,
                            is_active=question_data.is_active
                        )
                        
                        created_questions.append({
                            "id": str(question.id),
                            "question_text": question.question_text,
                            "question_type": question.question_type.value,
                            "is_required": question.is_required,
                            "order": question.order,
                            "placeholder_text": question.placeholder_text,
                            "is_active": question.is_active,
                            "created_at": question.created_at.isoformat(),
                            "updated_at": question.updated_at.isoformat()
                        })
                        
                    except Exception as e:
                        failed_questions.append({
                            "question_index": i,
                            "question_text": question_data.question_text,
                            "error": str(e)
                        })
                
                success = len(created_questions) > 0
                message = f"Successfully created {len(created_questions)} questions"
                if failed_questions:
                    message += f", {len(failed_questions)} failed"
                
                return BulkCreateResponse(
                    success=success,
                    message=message,
                    created_questions=created_questions,
                    failed_questions=failed_questions
                )
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create questions: {str(e)}")
    
    @staticmethod
    async def delete_question(question_id: str) -> dict:
        """Delete a screening question (Admin only)"""
        try:
            question = await ScreeningQuestion.get(id=question_id)
            question_order = question.order
            
            # Delete the question
            await question.delete()
            
            # Reorder remaining questions
            questions_to_update = await ScreeningQuestion.filter(order__gt=question_order).all()
            for q in questions_to_update:
                q.order -= 1
                await q.save()
            
            return {"message": "Question deleted successfully"}
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Question not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete question: {str(e)}")
    
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
                    phone=response_data.phone,
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
                    
                    elif question.question_type == QuestionType.YESNO:
                        if answer_data.answer_yesno is None:
                            if question.is_required:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Yes/No answer required for question: {question.question_text}"
                                )
                        else:
                            answer_value = answer_data.answer_yesno
                    
                    # Create the answer
                    await ScreeningAnswer.create(
                        response=response,
                        question=question,
                        answer_text=answer_data.answer_text,
                        answer_number=answer_data.answer_number,
                        answer_date=answer_data.answer_date,
                        answer_yesno=answer_data.answer_yesno
                    )
                
                # AUTO-GENERATE PROPERTY RECOMMENDATIONS
                try:
                    from controller.propertyRecommendationController import create_property_recommendation_from_screening
                    
                    print(f"🔄 Auto-generating property recommendations for screening: {response.id}")
                    
                    # Create recommendations in the background (don't fail screening if this fails)
                    recommendation_result = await create_property_recommendation_from_screening(str(response.id))
                    
                    property_count = recommendation_result.get('data', {}).get('property_count', 0)
                    match_score = recommendation_result.get('data', {}).get('match_score', 0)
                    
                    print(f"✅ Auto-generated {property_count} property recommendations (score: {match_score})")
                    
                    return {
                        "message": "Screening response submitted successfully",
                        "response_id": str(response.id),
                        "recommendations": {
                            "generated": True,
                            "property_count": property_count,
                            "match_score": match_score,
                            "message": f"Found {property_count} matching properties for you!"
                        }
                    }
                    
                except Exception as rec_error:
                    print(f"⚠️ Failed to auto-generate recommendations: {rec_error}")
                    # Don't fail the screening submission if recommendations fail
                    return {
                        "message": "Screening response submitted successfully",
                        "response_id": str(response.id),
                        "recommendations": {
                            "generated": False,
                            "message": "Recommendations will be generated shortly"
                        }
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
                        phone=response.phone,
                        answers_count=answer_count,
                        has_admin_reply=response.admin_reply is not None,
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
                elif answer.question.question_type == QuestionType.YESNO:
                    answer_value = answer.answer_yesno
                
                answer_list.append(
                    ScreeningAnswerResponse(
                        id=str(answer.id),
                        question_id=str(answer.question.id),
                        question_text=answer.question.question_text,
                        question_type=answer.question.question_type,
                        answer_text=answer.answer_text,
                        answer_number=answer.answer_number,
                        answer_date=answer.answer_date,
                        answer_yesno=answer.answer_yesno,
                        answer_value=answer_value,
                        created_at=answer.created_at.isoformat()
                    )
                )
            
            return ScreeningResponseDetail(
                id=str(response.id),
                full_name=response.full_name,
                email=response.email,
                phone=response.phone,
                message=response.message,
                admin_reply=response.admin_reply,
                replied_at=response.replied_at.isoformat() if response.replied_at else None,
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
    
    @staticmethod
    async def reply_to_response(response_id: str, reply_message: str) -> dict:
        """Reply to a screening response (Admin only)"""
        try:
            if not reply_message or not reply_message.strip():
                raise HTTPException(status_code=400, detail="Reply message is required")
            
            response = await ScreeningResponse.get(id=response_id)
            
            # Update the response with admin reply
            from datetime import datetime
            response.admin_reply = reply_message.strip()
            response.replied_at = datetime.now()
            await response.save()
            
            return {
                "message": "Reply sent successfully",
                "response_id": response_id,
                "reply_message": reply_message.strip(),
                "replied_at": response.replied_at.isoformat()
            }
            
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Response not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to send reply: {str(e)}")