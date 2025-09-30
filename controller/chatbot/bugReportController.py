from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class BugReportController:
    """Controller for bug report flow - 'Report an issue'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle bug report flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle all bug report questions in sequence
            bug_questions = [
                "what type of issue are you experiencing",
                "on which page did this happen",
                "what browser are you using",
                "can you describe what happened",
                "what's your email for updates"
            ]
            
            current_step = conversation.current_step
            
            # Store the response data
            await BugReportController._store_bug_data(conversation, current_message, user_response)
            
            # Check if we've completed all questions
            if current_step >= len(bug_questions):
                # End of flow - submit bug report
                return await BugReportController._submit_bug_report(conversation)
            
            # Continue with next question
            from .chatbotEngine import ChatbotFlowEngine
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, current_step)
            
            if not next_question_data:
                # End of flow
                return await BugReportController._submit_bug_report(conversation)
            
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
                    "message": "Next bug report question",
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
            print(f"❌ Error in bug report flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _store_bug_data(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Store bug report data based on question type"""
        try:
            question_text = current_message.question_text.lower()
            
            # Store data in conversation fields
            if "what type of issue are you experiencing" in question_text:
                conversation.guest_notes = f"Issue Type: {user_response}"
                
            elif "on which page did this happen" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nPage: {user_response}"
                
            elif "what browser are you using" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nBrowser: {user_response}"
                
            elif "can you describe what happened" in question_text:
                existing_notes = conversation.guest_notes or ""
                conversation.guest_notes = f"{existing_notes}\nDescription: {user_response}"
                
            elif "what's your email for updates" in question_text:
                conversation.guest_email = user_response
            
            await conversation.save()
            
        except Exception as e:
            print(f"❌ Error storing bug data: {e}")

    @staticmethod
    async def _submit_bug_report(conversation: ChatbotConversation):
        """Submit bug report and complete conversation"""
        try:
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Create bug report data
            try:
                bug_report = {
                    "session_id": conversation.session_id,
                    "bug_details": conversation.guest_notes or "No details provided",
                    "reporter_email": conversation.guest_email or "Not provided",
                    "user_agent": conversation.user_agent or "Not available",
                    "user_ip": conversation.user_ip or "Not available",
                    "flow_type": "bug_report",
                    "reported_at": datetime.now(timezone.utc).isoformat()
                }
                print(f"🐛 Bug report submitted: {bug_report}")
                
                # Here you would typically:
                # 1. Save to bug tracking system
                # 2. Send notification to development team
                # 3. Generate bug report ID
                # await create_bug_report_in_tracker(bug_report)
                # await send_bug_notification(dev_team_emails, bug_report)
                
            except Exception as e:
                print(f"⚠️ Failed to submit bug report: {e}")
            
            # Create completion message
            completion_step = conversation.current_step + 1
            completion_message = "Thank you for reporting this issue! 🐛 Our development team has been notified and will investigate. We'll send updates to your email address."
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=completion_step,
                question_text=completion_message
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Bug report submitted",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": completion_step,
                        "input_type": "bug_report_submitted",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "bug_report_submitted": True
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error submitting bug report: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)