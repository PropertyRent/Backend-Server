import uuid
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List, Optional
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus
from .chatbotEngine import ChatbotFlowEngine
from .propertySearchController import PropertySearchController
from .rentInquiryController import RentInquiryController
from .scheduleVisitController import ScheduleVisitController
from .chatbotScheduleVisitController import ChatbotScheduleVisitController
from .chatbotBugReportController import ChatbotBugReportController
from .chatbotFeedbackController import ChatbotFeedbackController
from .conversationController import ConversationController


class MainChatbotController:
    """Main chatbot controller handling conversation flow"""
    
    @staticmethod
    async def handle_start_chat(session_id: Optional[str] = None, user_agent: Optional[str] = None, user_ip: Optional[str] = None):
        """Start a new chat conversation or resume existing one"""
        try:
            # Check if session exists
            if session_id:
                conversation = await ChatbotConversation.get_or_none(session_id=session_id)
                if conversation and conversation.status == ConversationStatus.ACTIVE:
                    # Resume existing conversation
                    last_message = await ChatbotMessage.filter(conversation=conversation).order_by('-step_number').first()
                    if last_message and not last_message.user_response:
                        # Return the last unanswered question
                        return JSONResponse(
                            status_code=HTTP_200_OK,
                            content={
                                "success": True,
                                "message": "Conversation resumed",
                                "data": {
                                    "session_id": conversation.session_id,
                                    "question": last_message.question_text,
                                    "step_number": last_message.step_number,
                                    "input_type": "text",  # Default for resumed conversations
                                    "is_final": False,
                                    "flow_type": conversation.flow_type
                                }
                            }
                        )
            
            # Create new conversation
            new_session_id = session_id or str(uuid.uuid4())
            conversation = await ChatbotConversation.create(
                session_id=new_session_id,
                user_agent=user_agent,
                user_ip=user_ip
            )
            
            # Get initial question
            initial_question = ChatbotFlowEngine.get_initial_question()
            
            # Save initial message
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=0,
                question_text=initial_question["question"]
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Chat started successfully",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": initial_question["question"],
                        "options": initial_question["options"],
                        "step_number": initial_question["step_number"],
                        "input_type": initial_question["input_type"],
                        "is_final": initial_question["is_final"],
                        "flow_type": None
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error starting chat: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start chat: {str(e)}"
            )

    @staticmethod
    async def handle_chat_response(session_id: str, user_response: str):
        """Process user response and return next question"""
        try:
            # Get conversation
            conversation = await ChatbotConversation.get_or_none(session_id=session_id)
            if not conversation:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            if conversation.status != ConversationStatus.ACTIVE:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Conversation is not active"
                )
            
            # Get current message and update with response
            current_message = await ChatbotMessage.filter(
                conversation=conversation
            ).order_by('-step_number').first()
            
            if current_message and not current_message.user_response:
                current_message.user_response = user_response
                current_message.responded_at = datetime.now(timezone.utc)
                await current_message.save()
                
                # Calculate response time
                if current_message.created_at:
                    created_at = current_message.created_at
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    
                    responded_at = current_message.responded_at
                    if responded_at.tzinfo is None:
                        responded_at = responded_at.replace(tzinfo=timezone.utc)
                    
                    response_time = (responded_at - created_at).total_seconds()
                    current_message.response_time_seconds = int(response_time)
                    await current_message.save()
                
                # Determine flow if this is the first response
                if conversation.current_step == 0 and not conversation.flow_type:
                    flow_type = ChatbotFlowEngine.determine_flow_from_response(user_response)
                    conversation.flow_type = flow_type
                    await conversation.save()
                    print(f"🔄 Flow determined: {flow_type} for response: {user_response}")
                
                # Route to appropriate controller based on flow type
                if conversation.flow_type == "property_search":
                    return await PropertySearchController.handle_response(conversation, current_message, user_response)
                elif conversation.flow_type == "rent_inquiry":
                    return await RentInquiryController.handle_response(conversation, current_message, user_response)
                elif conversation.flow_type == "schedule_visit":
                    return await ChatbotScheduleVisitController.handle_response(conversation, current_message, user_response)
                elif conversation.flow_type == "bug_report":
                    return await ChatbotBugReportController.handle_response(conversation, current_message, user_response)
                elif conversation.flow_type == "feedback":
                    return await ChatbotFeedbackController.handle_response(conversation, current_message, user_response)
                else:
                    # Default handling - continue with standard flow
                    return await MainChatbotController._handle_standard_flow(conversation, user_response)
            
            # Handle edge case where message already has response
            return await MainChatbotController._handle_standard_flow(conversation, user_response)
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error processing chat response: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process response: {str(e)}"
            )

    @staticmethod
    async def _handle_standard_flow(conversation, user_response: str):
        """Handle standard conversation flow"""
        try:
            # Get next question based on current step in the specific flow
            flow_question_index = conversation.current_step
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, flow_question_index)
            
            if not next_question_data:
                # End of flow - show satisfaction question
                return await ConversationController.handle_satisfaction_question(conversation)
            
            # Create next message
            next_step_number = conversation.current_step + 1
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step_number,
                question_text=next_question_data["question"]
            )
            
            # Update conversation step
            conversation.current_step += 1
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Next question retrieved",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": next_question_data["question"],
                        "options": next_question_data.get("options"),
                        "step_number": next_step_number,
                        "input_type": next_question_data["input_type"],
                        "is_final": next_question_data["is_final"],
                        "flow_type": conversation.flow_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error in standard flow: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to handle standard flow: {str(e)}"
            )

    @staticmethod
    async def handle_satisfaction_response(session_id: str, is_satisfied: bool, feedback: Optional[str] = None):
        """Handle final satisfaction response"""
        return await ConversationController.handle_satisfaction_response(session_id, is_satisfied, feedback)

    @staticmethod
    async def handle_get_conversations(page: int = 1, limit: int = 20, status: Optional[str] = None):
        """Get all conversations for admin dashboard"""
        return await ConversationController.handle_get_conversations(page, limit, status)

    @staticmethod
    async def handle_get_conversation_details(conversation_id: str):
        """Get detailed conversation with all messages"""
        return await ConversationController.handle_get_conversation_details(conversation_id)