from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class GeneralSupportController:
    """Controller for general support flow - 'General support'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle general support flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle all general support questions in sequence
            support_questions = [
                "what do you need help with",
                "can you describe your issue briefly",
                "how urgent is this matter",
                "what's the best way to reach you"
            ]
            
            current_step = conversation.current_step
            
            # Store the response data
            await GeneralSupportController._store_support_data(conversation, current_message, user_response)
            
            # Check if we've completed all questions
            if current_step >= len(support_questions):
                # End of flow - create support ticket
                return await GeneralSupportController._create_support_ticket(conversation)
            
            # Continue with next question
            from .chatbotEngine import ChatbotFlowEngine
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, current_step)
            
            if not next_question_data:
                # End of flow
                return await GeneralSupportController._create_support_ticket(conversation)
            
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
                    "message": "Next support question",
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
            print(f"❌ Error in general support flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _store_support_data(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Store support data based on question type"""
        try:
            question_text = current_message.question_text.lower()
            
            # Store data in conversation fields
            if "what do you need help with" in question_text:
                conversation.guest_notes = f"Issue Type: {user_response}"
                
            elif "can you describe your issue briefly" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nDescription: {user_response}"
                
            elif "how urgent is this matter" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nUrgency: {user_response}"
                
            elif "what's the best way to reach you" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nPreferred Contact: {user_response}"
                conversation.guest_name = user_response  # Store contact method
            
            await conversation.save()
            
        except Exception as e:
            print(f"❌ Error storing support data: {e}")

    @staticmethod
    async def _create_support_ticket(conversation: ChatbotConversation):
        """Create support ticket and complete conversation"""
        try:
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Create support ticket data
            try:
                support_ticket = {
                    "session_id": conversation.session_id,
                    "issue_details": conversation.guest_notes or "No details provided",
                    "contact_method": conversation.guest_name or "Not specified",
                    "user_email": conversation.guest_email or "Not provided",
                    "flow_type": "general_support",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                print(f"🎫 Support ticket created: {support_ticket}")
                
                # Here you would typically:
                # 1. Save to support ticket database
                # 2. Send notification to support team
                # 3. Generate ticket ID
                # await create_support_ticket_in_db(support_ticket)
                # await send_support_notification(admin_emails, support_ticket)
                
            except Exception as e:
                print(f"⚠️ Failed to create support ticket: {e}")
            
            # Create completion message
            completion_step = conversation.current_step + 1
            completion_message = "Thank you! Your support request has been submitted. Our team will get back to you shortly based on your preferred contact method. 🎫"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=completion_step,
                question_text=completion_message
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Support ticket created",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": completion_step,
                        "input_type": "support_ticket_created",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "support_ticket_created": True
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error creating support ticket: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)