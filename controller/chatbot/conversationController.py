from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List, Optional
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ChatbotEscalation, ConversationStatus
from model.userModel import User, UserRole
from schemas.chatbotSchemas import ChatbotResponse, ConversationSummary, MessageSummary, EscalationSummary


class ConversationController:
    """Controller for conversation management and admin functions"""
    
    @staticmethod
    async def handle_satisfaction_question(conversation: ChatbotConversation):
        """Handle satisfaction question at the end of flows"""
        try:
            satisfaction_step = conversation.current_step + 1
            satisfaction_question = "Are you satisfied with the assistance provided?"
            
            # Create satisfaction message
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=satisfaction_step,
                question_text=satisfaction_question
            )
            
            conversation.current_step = satisfaction_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Satisfaction question presented",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": satisfaction_question,
                        "options": ["Yes, I'm satisfied", "No, I need more help"],
                        "step_number": satisfaction_step,
                        "input_type": "choice",
                        "is_final": True,
                        "flow_type": conversation.flow_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling satisfaction question: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to handle satisfaction question: {str(e)}"
            )

    @staticmethod
    async def handle_satisfaction_response(session_id: str, is_satisfied: bool, feedback: Optional[str] = None):
        """Handle final satisfaction response"""
        try:
            # Get conversation
            conversation = await ChatbotConversation.get_or_none(session_id=session_id)
            if not conversation:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Update satisfaction
            conversation.is_satisfied = is_satisfied
            conversation.completed_at = datetime.now(timezone.utc)
            
            if is_satisfied:
                conversation.status = ConversationStatus.COMPLETED
            else:
                conversation.status = ConversationStatus.ESCALATED
            
            await conversation.save()
            
            # Update last message with satisfaction response
            last_message = await ChatbotMessage.filter(
                conversation=conversation
            ).order_by('-step_number').first()
            
            if last_message:
                satisfaction_text = "Yes, I'm satisfied" if is_satisfied else "No, I need more help"
                if feedback:
                    satisfaction_text += f" - {feedback}"
                
                last_message.user_response = satisfaction_text
                last_message.responded_at = datetime.now(timezone.utc)
                await last_message.save()
            
            # If not satisfied, create escalation
            if not is_satisfied:
                await ChatbotEscalation.create(
                    conversation=conversation,
                    reason="unsatisfied",
                    priority="medium",
                    contact_email=conversation.guest_email or "unknown@example.com",
                    contact_name=conversation.guest_name or "Anonymous User"
                )
            
            # Send email notification to admin
            await ConversationController._send_admin_notifications(conversation, is_satisfied)
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Thank you for your feedback!" if is_satisfied else "We'll have someone contact you soon!",
                    "data": {
                        "conversation_completed": True,
                        "escalated": not is_satisfied,
                        "session_id": session_id
                    }
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error handling satisfaction: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to handle satisfaction: {str(e)}"
            )

    @staticmethod
    async def _send_admin_notifications(conversation: ChatbotConversation, is_satisfied: bool):
        """Send email notifications to admin users"""
        try:
            # Get all admin emails
            admin_users = await User.filter(role__in=[UserRole.ADMIN, UserRole.ADMIN_PLUS, UserRole.SUPERADMIN])
            admin_emails = [admin.email for admin in admin_users if admin.email]
            
            if admin_emails:
                # Get conversation messages for email
                messages = await ChatbotMessage.filter(conversation=conversation).order_by('step_number')
                messages_data = [
                    {
                        "question": msg.question_text,
                        "answer": msg.user_response,
                        "response_time": msg.response_time_seconds
                    }
                    for msg in messages if msg.user_response  # Only include answered questions
                ]
                
                conversation_data = {
                    "session_id": conversation.session_id,
                    "flow_type": conversation.flow_type,
                    "user_name": conversation.guest_name or "Anonymous",
                    "user_email": conversation.guest_email or "Not provided",
                    "created_at": conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Send appropriate email
                for admin_email in admin_emails:
                    try:
                        if is_satisfied:
                            # Import and send satisfaction summary
                            from emailService.chatbotEmail import send_satisfaction_summary
                            await send_satisfaction_summary(admin_email, conversation_data, messages_data, True)
                        else:
                            # Import and send escalation notification
                            from emailService.chatbotEmail import send_escalation_notification
                            await send_escalation_notification(admin_email, conversation_data, messages_data, "unsatisfied")
                    except ImportError:
                        print(f"⚠️ Email service not available")
                        break
                    except Exception as email_error:
                        print(f"⚠️ Failed to send email to {admin_email}: {email_error}")
                        continue
                        
        except Exception as email_error:
            print(f"⚠️ Failed to send email notifications: {email_error}")
            # Don't fail the entire request if email fails

    @staticmethod
    async def handle_get_conversations(page: int = 1, limit: int = 20, status: Optional[str] = None):
        """Get all conversations for admin dashboard"""
        try:
            query = ChatbotConversation.all()
            
            if status:
                query = query.filter(status=status)
            
            # Pagination
            offset = (page - 1) * limit
            conversations = await query.offset(offset).limit(limit).prefetch_related('messages', 'escalations')
            
            total_count = await ChatbotConversation.all().count()
            
            conversations_data = []
            for conv in conversations:
                conversations_data.append({
                    "id": str(conv.id),
                    "session_id": conv.session_id,
                    "flow_type": conv.flow_type,
                    "status": conv.status,
                    "is_satisfied": conv.is_satisfied,
                    "user_name": conv.guest_name,
                    "user_email": conv.guest_email,
                    "created_at": conv.created_at.isoformat(),
                    "completed_at": conv.completed_at.isoformat() if conv.completed_at else None,
                    "messages_count": len(conv.messages),
                    "has_escalation": len(conv.escalations) > 0
                })
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Conversations retrieved successfully",
                    "data": {
                        "conversations": conversations_data,
                        "pagination": {
                            "page": page,
                            "limit": limit,
                            "total": total_count,
                            "pages": (total_count + limit - 1) // limit
                        }
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversations: {str(e)}"
            )

    @staticmethod
    async def handle_get_conversation_details(conversation_id: str):
        """Get detailed conversation with all messages"""
        try:
            conversation = await ChatbotConversation.get_or_none(id=conversation_id).prefetch_related('messages', 'escalations')
            
            if not conversation:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Get messages
            messages_data = []
            for msg in sorted(conversation.messages, key=lambda x: x.step_number):
                messages_data.append({
                    "step_number": msg.step_number,
                    "question": msg.question_text,
                    "answer": msg.user_response,
                    "response_time": msg.response_time_seconds,
                    "created_at": msg.created_at.isoformat(),
                    "responded_at": msg.responded_at.isoformat() if msg.responded_at else None
                })
            
            # Get escalations
            escalations_data = []
            for esc in conversation.escalations:
                escalations_data.append({
                    "id": str(esc.id),
                    "reason": esc.reason,
                    "priority": esc.priority,
                    "status": esc.status,
                    "contact_name": esc.contact_name,
                    "contact_email": esc.contact_email,
                    "created_at": esc.created_at.isoformat(),
                    "resolved_at": esc.resolved_at.isoformat() if esc.resolved_at else None
                })
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Conversation details retrieved",
                    "data": {
                        "conversation": {
                            "id": str(conversation.id),
                            "session_id": conversation.session_id,
                            "flow_type": conversation.flow_type,
                            "status": conversation.status,
                            "is_satisfied": conversation.is_satisfied,
                            "user_name": conversation.guest_name,
                            "user_email": conversation.guest_email,
                            "created_at": conversation.created_at.isoformat(),
                            "completed_at": conversation.completed_at.isoformat() if conversation.completed_at else None,
                        },
                        "messages": messages_data,
                        "escalations": escalations_data
                    }
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error getting conversation details: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation details: {str(e)}"
            )