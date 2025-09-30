from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class ChatbotFeedbackController:
    """Controller for chatbot feedback flow with dynamic categorization and ratings"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle feedback flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle initial flow setup - when user just selected "Give feedback"
            if "hi! i'm your property assistant" in question_text or conversation.current_step == 0:
                return await ChatbotFeedbackController._start_feedback_flow(conversation)
            
            # Step 1: What area would you like to give feedback about?
            if "what area would you like to give feedback about" in question_text:
                return await ChatbotFeedbackController._handle_feedback_category_selection(conversation, user_response)
            
            # Step 2: Rate your experience
            elif "please rate your experience" in question_text or "how would you rate" in question_text:
                return await ChatbotFeedbackController._handle_rating_selection(conversation, user_response)
            
            # Step 3: Detailed feedback
            elif ("please share your detailed feedback" in question_text or 
                  "what specifically" in question_text or
                  "what aspects" in question_text or
                  "what did you like" in question_text or
                  "how can we improve" in question_text or
                  "what improvements would you like" in question_text):
                return await ChatbotFeedbackController._handle_detailed_feedback(conversation, user_response)
            
            # Step 4: Suggestions for improvement
            elif ("any suggestions for improvement" in question_text or 
                  "suggestions" in question_text and "improvement" in question_text):
                return await ChatbotFeedbackController._handle_improvement_suggestions(conversation, user_response)
            
            # Step 5: Contact information (optional)
            elif "would you like us to follow up" in question_text:
                return await ChatbotFeedbackController._handle_followup_preference(conversation, user_response)
            
            # Step 6: Email collection (if follow-up requested)
            elif "please provide your email" in question_text:
                return await ChatbotFeedbackController._handle_contact_info(conversation, user_response)
            
            # Default: Move to next step
            return await ChatbotFeedbackController._handle_default_flow(conversation, user_response)
            
        except Exception as e:
            print(f"❌ Error in chatbot feedback flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _start_feedback_flow(conversation: ChatbotConversation):
        """Start the feedback flow"""
        try:
            next_step = conversation.current_step + 1
            category_question = "What area would you like to give feedback about?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=category_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Starting feedback flow",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": category_question,
                        "options": [
                            "Property search experience",
                            "Website usability", 
                            "Property listings quality",
                            "Customer support",
                            "Property visit experience",
                            "Overall service"
                        ],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error starting feedback flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _handle_feedback_category_selection(conversation: ChatbotConversation, user_response: str):
        """Handle feedback category selection and ask for rating"""
        try:
            # Store feedback category in guest_email field
            conversation.guest_email = f"CATEGORY:{user_response}"
            
            # Use standardized rating question for all categories
            next_step = conversation.current_step + 1
            rating_question = f"Please rate your experience with {user_response.lower()}:"
            context = f"{user_response.lower()}"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=rating_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Feedback category selected, asking for rating",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": rating_question,
                        "options": [
                            "⭐⭐⭐⭐⭐ Excellent (5/5)",
                            "⭐⭐⭐⭐ Good (4/5)",
                            "⭐⭐⭐ Average (3/5)",
                            "⭐⭐ Poor (2/5)",
                            "⭐ Very Poor (1/5)"
                        ],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "feedback_category": user_response,
                        "rating_context": context
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling feedback category selection: {e}")
            raise

    @staticmethod
    async def _handle_rating_selection(conversation: ChatbotConversation, user_response: str):
        """Handle rating selection and ask for detailed feedback"""
        try:
            # Store rating by appending to stored data
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|RATING:{user_response}"
            
            # Extract category for personalized question
            category = ""
            if "CATEGORY:" in stored_data:
                category = stored_data.replace("CATEGORY:", "").split("|")[0]
            
            # Extract rating value for personalized response
            rating_value = "3"  # default
            if "(5/5)" in user_response:
                rating_value = "5"
            elif "(4/5)" in user_response:
                rating_value = "4"
            elif "(3/5)" in user_response:
                rating_value = "3"
            elif "(2/5)" in user_response:
                rating_value = "2"
            elif "(1/5)" in user_response:
                rating_value = "1"
            
            # Use standardized detailed feedback question for all categories
            next_step = conversation.current_step + 1
            
            if int(rating_value) >= 4:
                details_question = f"Great! What specifically did you like about our {category.lower()}?"
            else:
                details_question = f"What would you like us to improve about our {category.lower()}?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=details_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Rating received, asking for detailed feedback",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": details_question,
                        "step_number": next_step,
                        "input_type": "text",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "feedback_category": category,
                        "rating": rating_value,
                        "placeholder": "Share your detailed thoughts and feedback"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling rating selection: {e}")
            raise

    @staticmethod
    async def _handle_detailed_feedback(conversation: ChatbotConversation, user_response: str):
        """Handle detailed feedback and ask for improvement suggestions"""
        try:
            # Store detailed feedback
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|DETAILS:{user_response}"
            
            # Get rating to determine if we should ask for improvements or not
            rating_value = "3"  # default
            if "|RATING:" in stored_data:
                rating_text = stored_data.split("|RATING:")[1].split("|")[0]
                if "(5/5)" in rating_text:
                    rating_value = "5"
                elif "(4/5)" in rating_text:
                    rating_value = "4"
                elif "(3/5)" in rating_text:
                    rating_value = "3"
                elif "(2/5)" in rating_text:
                    rating_value = "2"
                elif "(1/5)" in rating_text:
                    rating_value = "1"
            
            next_step = conversation.current_step + 1
            
            # For high ratings, ask for suggestions. For low ratings, skip to follow-up
            if int(rating_value) >= 4:
                suggestions_question = "Any suggestions for improvement or new features you'd like to see?"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=suggestions_question
                )
                
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Detailed feedback received, asking for suggestions",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": suggestions_question,
                            "step_number": next_step,
                            "input_type": "text",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "rating": rating_value,
                            "placeholder": "Share any suggestions or ideas for improvement"
                        }
                    }
                )
            else:
                # Skip suggestions for low ratings, go directly to follow-up
                return await ChatbotFeedbackController._ask_followup_preference(conversation)
                
        except Exception as e:
            print(f"❌ Error handling detailed feedback: {e}")
            raise

    @staticmethod
    async def _handle_improvement_suggestions(conversation: ChatbotConversation, user_response: str):
        """Handle improvement suggestions and ask about follow-up"""
        try:
            # Store suggestions
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|SUGGESTIONS:{user_response}"
            
            return await ChatbotFeedbackController._ask_followup_preference(conversation)
            
        except Exception as e:
            print(f"❌ Error handling improvement suggestions: {e}")
            raise

    @staticmethod
    async def _ask_followup_preference(conversation: ChatbotConversation):
        """Ask if user wants follow-up contact"""
        try:
            next_step = conversation.current_step + 1
            followup_question = "Would you like us to follow up with you about your feedback?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=followup_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Asking about follow-up preference",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": followup_question,
                        "options": [
                            "Yes, please contact me",
                            "No, thank you"
                        ],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error asking followup preference: {e}")
            raise

    @staticmethod
    async def _handle_followup_preference(conversation: ChatbotConversation, user_response: str):
        """Handle follow-up preference"""
        try:
            # Store follow-up preference
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|FOLLOWUP:{user_response}"
            
            if user_response.lower() == "yes, please contact me":
                # Ask for email
                next_step = conversation.current_step + 1
                email_question = "Please provide your email address so we can follow up with you:"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=email_question
                )
                
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Follow-up requested, asking for email",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": email_question,
                            "step_number": next_step,
                            "input_type": "email",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "placeholder": "Enter your email address"
                        }
                    }
                )
            else:
                # Complete feedback without follow-up
                return await ChatbotFeedbackController._complete_feedback(conversation, None)
                
        except Exception as e:
            print(f"❌ Error handling followup preference: {e}")
            raise

    @staticmethod
    async def _handle_contact_info(conversation: ChatbotConversation, user_response: str):
        """Handle contact info and complete feedback"""
        try:
            return await ChatbotFeedbackController._complete_feedback(conversation, user_response)
            
        except Exception as e:
            print(f"❌ Error handling contact info: {e}")
            raise

    @staticmethod
    async def _complete_feedback(conversation: ChatbotConversation, user_email: str = None):
        """Complete the feedback submission"""
        try:
            # Parse all stored data
            stored_data = conversation.guest_email or ""
            
            # Extract information
            category = ""
            rating = ""
            details = ""
            suggestions = ""
            followup = ""
            
            parts = stored_data.split("|")
            for part in parts:
                if part.startswith("CATEGORY:"):
                    category = part.replace("CATEGORY:", "")
                elif part.startswith("RATING:"):
                    rating = part.replace("RATING:", "")
                elif part.startswith("DETAILS:"):
                    details = part.replace("DETAILS:", "")
                elif part.startswith("SUGGESTIONS:"):
                    suggestions = part.replace("SUGGESTIONS:", "")
                elif part.startswith("FOLLOWUP:"):
                    followup = part.replace("FOLLOWUP:", "")
            
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            if user_email:
                conversation.guest_name = user_email  # Store email for admin reference
            await conversation.save()
            
            # Submit feedback to admin
            try:
                feedback_data = {
                    "category": category,
                    "rating": rating,
                    "details": details,
                    "suggestions": suggestions or "No suggestions provided",
                    "followup_requested": followup == "Yes, please contact me",
                    "user_email": user_email or "No contact requested",
                    "session_id": conversation.session_id,
                    "submitted_at": datetime.now(timezone.utc).isoformat()
                }
                print(f"💬 Feedback submitted: {feedback_data}")
                
                # Here you would send feedback to admin team
                # await send_feedback_notification(admin_emails, feedback_data)
                
            except Exception as e:
                print(f"⚠️ Failed to send feedback notification: {e}")
            
            # Create completion message
            if user_email:
                completion_message = f"Thank you for your valuable feedback! 🌟 We've received your {rating.split('(')[0].strip()} rating for '{category}'. We'll review your feedback and contact you at {user_email} if needed."
            else:
                completion_message = f"Thank you for your valuable feedback! 🌟 We've received your {rating.split('(')[0].strip()} rating for '{category}'. Your input helps us improve our platform!"
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Feedback submitted successfully",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": conversation.current_step + 1,
                        "input_type": "feedback_submitted",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "feedback_submitted": True,
                        "feedback_summary": {
                            "category": category,
                            "rating": rating,
                            "followup_requested": user_email is not None,
                            "user_email": user_email or "No contact requested"
                        }
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error completing feedback: {e}")
            raise

    @staticmethod
    async def _handle_default_flow(conversation: ChatbotConversation, user_response: str):
        """Handle default flow when no specific question matches"""
        try:
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)
        except Exception as e:
            print(f"❌ Error in default flow: {e}")
            raise