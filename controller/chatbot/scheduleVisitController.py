from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class ScheduleVisitController:
    """Controller for schedule visit flow - 'Schedule a property visit'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle schedule visit flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle all schedule visit questions in sequence
            schedule_questions = [
                "which property would you like to visit",
                "what's your preferred date",
                "what time works best for you",
                "what's your full name",
                "what's your contact number",
                "what's your email address"
            ]
            
            current_step = conversation.current_step
            
            # Store the response data
            await ScheduleVisitController._store_visit_data(conversation, current_message, user_response)
            
            # Check if we've completed all questions
            if current_step >= len(schedule_questions):
                # End of flow - schedule the visit
                return await ScheduleVisitController._complete_visit_scheduling(conversation)
            
            # Continue with next question
            from .chatbotEngine import ChatbotFlowEngine
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, current_step)
            
            if not next_question_data:
                # End of flow
                return await ScheduleVisitController._complete_visit_scheduling(conversation)
            
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
                    "message": "Next visit scheduling question",
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
            print(f"❌ Error in schedule visit flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _store_visit_data(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Store visit scheduling data based on question type"""
        try:
            question_text = current_message.question_text.lower()
            
            # Store data in conversation fields (reusing existing fields creatively)
            if "which property would you like to visit" in question_text:
                # Store property name in a custom field (you might need to add this to model)
                conversation.guest_notes = f"Property: {user_response}"
                
            elif "what's your preferred date" in question_text:
                # Append date to notes
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nDate: {user_response}"
                
            elif "what time works best" in question_text:
                # Append time to notes
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nTime: {user_response}"
                
            elif "what's your full name" in question_text:
                conversation.guest_name = user_response
                
            elif "what's your contact number" in question_text:
                # Store phone in notes since we use guest_name for actual name
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nPhone: {user_response}"
                
            elif "what's your email address" in question_text:
                conversation.guest_email = user_response
            
            await conversation.save()
            
        except Exception as e:
            print(f"❌ Error storing visit data: {e}")

    @staticmethod
    async def _complete_visit_scheduling(conversation: ChatbotConversation):
        """Complete the visit scheduling process"""
        try:
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Send visit scheduling notification to admin
            try:
                visit_data = {
                    "session_id": conversation.session_id,
                    "visitor_name": conversation.guest_name or "Not provided",
                    "visitor_email": conversation.guest_email or "Not provided",
                    "visit_details": conversation.guest_notes or "No details provided",
                    "flow_type": "schedule_visit"
                }
                print(f"📅 Visit scheduled: {visit_data}")
                
                # Here you would typically send an email notification to admin
                # await send_visit_scheduling_notification(admin_emails, visit_data)
                
            except Exception as e:
                print(f"⚠️ Failed to send visit scheduling notification: {e}")
            
            # Create completion message
            completion_step = conversation.current_step + 1
            completion_message = "Thank you! Your property visit has been scheduled. Our team will contact you shortly to confirm the details. 📅"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=completion_step,
                question_text=completion_message
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Visit scheduling completed",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": completion_step,
                        "input_type": "visit_scheduled",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "visit_scheduled": True
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error completing visit scheduling: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)