from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class FeedbackController:
    """Controller for feedback flow - 'Give feedback'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle feedback flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle all feedback questions in sequence
            feedback_questions = [
                "what would you like to give feedback about",
                "how would you rate your experience",
                "what did you like most",
                "what can we improve",
                "would you recommend us to others"
            ]
            
            current_step = conversation.current_step
            
            # Store the response data
            await FeedbackController._store_feedback_data(conversation, current_message, user_response)
            
            # Check if we've completed all questions
            if current_step >= len(feedback_questions):
                # End of flow - submit feedback
                return await FeedbackController._submit_feedback(conversation)
            
            # Continue with next question
            from .chatbotEngine import ChatbotFlowEngine
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, current_step)
            
            if not next_question_data:
                # End of flow
                return await FeedbackController._submit_feedback(conversation)
            
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
                    "message": "Next feedback question",
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
            print(f"❌ Error in feedback flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _store_feedback_data(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Store feedback data based on question type"""
        try:
            question_text = current_message.question_text.lower()
            
            # Store data in conversation fields
            if "what would you like to give feedback about" in question_text:
                conversation.guest_notes = f"Feedback Category: {user_response}"
                
            elif "how would you rate your experience" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nRating: {user_response}"
                
            elif "what did you like most" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nLiked Most: {user_response}"
                
            elif "what can we improve" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nImprovement Suggestions: {user_response}"
                
            elif "would you recommend us to others" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nRecommendation: {user_response}"
            
            await conversation.save()
            
        except Exception as e:
            print(f"❌ Error storing feedback data: {e}")

    @staticmethod
    async def _submit_feedback(conversation: ChatbotConversation):
        """Submit feedback and complete conversation"""
        try:
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Create feedback data
            try:
                feedback_data = {
                    "session_id": conversation.session_id,
                    "feedback_details": conversation.guest_notes or "No feedback provided",
                    "user_email": conversation.guest_email or "Anonymous",
                    "flow_type": "feedback",
                    "submitted_at": datetime.now(timezone.utc).isoformat()
                }
                print(f"💬 Feedback submitted: {feedback_data}")
                
                # Here you would typically:
                # 1. Save to feedback database
                # 2. Send notification to management team
                # 3. Analyze sentiment and categorize
                # await save_feedback_to_db(feedback_data)
                # await send_feedback_notification(management_emails, feedback_data)
                
            except Exception as e:
                print(f"⚠️ Failed to submit feedback: {e}")
            
            # Create completion message
            completion_step = conversation.current_step + 1
            completion_message = "Thank you so much for your valuable feedback! 💬 Your input helps us improve our services. We truly appreciate you taking the time to share your thoughts with us!"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=completion_step,
                question_text=completion_message
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Feedback submitted successfully",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": completion_step,
                        "input_type": "feedback_submitted",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "feedback_submitted": True
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error submitting feedback: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)