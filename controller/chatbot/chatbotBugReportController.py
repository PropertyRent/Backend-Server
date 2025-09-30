from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus


class ChatbotBugReportController:
    """Controller for chatbot bug report flow with dynamic issue categorization"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle bug report flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle initial flow setup - when user just selected "Report an issue"
            if "hi! i'm your property assistant" in question_text or conversation.current_step == 0:
                return await ChatbotBugReportController._start_bug_report_flow(conversation)
            
            # Step 1: What type of issue would you like to report?
            if "what type of issue would you like to report" in question_text:
                return await ChatbotBugReportController._handle_issue_type_selection(conversation, user_response)
            
            # Step 2: Category-specific questions
            elif ("can you provide more details" in question_text or 
                  "please describe" in question_text or 
                  "please provide details" in question_text):
                return await ChatbotBugReportController._handle_issue_details(conversation, user_response)
            
            # Step 3: Technical details (for technical issues)
            elif "what device/browser are you using" in question_text:
                return await ChatbotBugReportController._handle_technical_details(conversation, user_response)
            
            # Step 4: Priority/Urgency
            elif "how urgent is this issue" in question_text:
                return await ChatbotBugReportController._handle_urgency_selection(conversation, user_response)
            
            # Step 5: Contact information
            elif "what's your email" in question_text or "please provide your email" in question_text:
                return await ChatbotBugReportController._handle_contact_info(conversation, user_response)
            
            # Default: Move to next step
            return await ChatbotBugReportController._handle_default_flow(conversation, user_response)
            
        except Exception as e:
            print(f"❌ Error in chatbot bug report flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _start_bug_report_flow(conversation: ChatbotConversation):
        """Start the bug report flow"""
        try:
            next_step = conversation.current_step + 1
            issue_type_question = "What type of issue would you like to report?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=issue_type_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Starting bug report flow",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": issue_type_question,
                        "options": [
                            "Website bug",
                            "Property not found error", 
                            "Search not working",
                            "Other technical issue"
                        ],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error starting bug report flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _handle_issue_type_selection(conversation: ChatbotConversation, user_response: str):
        """Handle issue type selection and ask category-specific questions"""
        try:
            # Store issue type in guest_email field
            conversation.guest_email = f"ISSUE_TYPE:{user_response}"
            
            # Generate category-specific follow-up question
            next_step = conversation.current_step + 1
            
            if user_response.lower() in ["website bug", "search not working", "other technical issue"]:
                details_question = "Please describe what exactly happened. Include steps to reproduce the issue if possible:"
                input_type = "text"
                placeholder = "Describe the technical issue in detail"
                
            elif user_response.lower() == "property not found error":
                details_question = "Please provide details about the property search issue:"
                input_type = "text"
                placeholder = "Describe the property search problem (e.g., property not showing up, incorrect search results)"
                
            else:
                details_question = "Please provide more details about the issue:"
                input_type = "text"
                placeholder = "Describe your issue in detail"
            
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
                    "message": "Issue type selected, asking for details",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": details_question,
                        "step_number": next_step,
                        "input_type": input_type,
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "issue_type": user_response,
                        "placeholder": placeholder
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling issue type selection: {e}")
            raise

    @staticmethod
    async def _handle_issue_details(conversation: ChatbotConversation, user_response: str):
        """Handle issue details and ask for technical information if needed"""
        try:
            # Store issue details by appending to stored data
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|DETAILS:{user_response}"
            
            # Check if we need technical details (for technical issues)
            issue_type = stored_data.replace("ISSUE_TYPE:", "") if "ISSUE_TYPE:" in stored_data else ""
            
            next_step = conversation.current_step + 1
            
            if issue_type.lower() in ["website bug", "search not working", "other technical issue"]:
                # Ask for technical details
                tech_question = "What device/browser are you using? (This helps us reproduce the issue)"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=tech_question
                )
                
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Issue details received, asking for technical info",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": tech_question,
                            "options": [
                                "Chrome on Windows",
                                "Chrome on Mac", 
                                "Safari on Mac",
                                "Firefox on Windows",
                                "Mobile app on Android",
                                "Mobile app on iOS",
                                "Other"
                            ],
                            "step_number": next_step,
                            "input_type": "choice",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "issue_type": issue_type
                        }
                    }
                )
            else:
                # Skip technical details, go to urgency
                return await ChatbotBugReportController._ask_urgency(conversation, issue_type)
                
        except Exception as e:
            print(f"❌ Error handling issue details: {e}")
            raise

    @staticmethod
    async def _handle_technical_details(conversation: ChatbotConversation, user_response: str):
        """Handle technical details and move to urgency"""
        try:
            # Store technical details
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|TECH:{user_response}"
            
            # Get issue type for urgency question
            issue_type = ""
            if "ISSUE_TYPE:" in stored_data:
                issue_type = stored_data.split("ISSUE_TYPE:")[1].split("|")[0]
            
            return await ChatbotBugReportController._ask_urgency(conversation, issue_type)
            
        except Exception as e:
            print(f"❌ Error handling technical details: {e}")
            raise

    @staticmethod
    async def _ask_urgency(conversation: ChatbotConversation, issue_type: str):
        """Ask about issue urgency"""
        try:
            next_step = conversation.current_step + 1
            urgency_question = "How urgent is this issue for you?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=urgency_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Technical details received, asking about urgency",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": urgency_question,
                        "options": [
                            "Critical - Blocking my usage",
                            "High - Significant impact",
                            "Medium - Minor inconvenience", 
                            "Low - When convenient"
                        ],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "issue_type": issue_type
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error asking urgency: {e}")
            raise

    @staticmethod
    async def _handle_urgency_selection(conversation: ChatbotConversation, user_response: str):
        """Handle urgency selection and ask for contact info"""
        try:
            # Store urgency
            stored_data = conversation.guest_email or ""
            conversation.guest_email = f"{stored_data}|URGENCY:{user_response}"
            
            next_step = conversation.current_step + 1
            contact_question = "Please provide your email address so we can follow up on this issue:"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=contact_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Urgency selected, asking for contact info",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": contact_question,
                        "step_number": next_step,
                        "input_type": "email",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "urgency": user_response,
                        "placeholder": "Enter your email address"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling urgency selection: {e}")
            raise

    @staticmethod
    async def _handle_contact_info(conversation: ChatbotConversation, user_response: str):
        """Handle contact info and complete bug report"""
        try:
            # Parse all stored data
            stored_data = conversation.guest_email or ""
            user_email = user_response
            
            # Extract information
            issue_type = ""
            issue_details = ""
            technical_info = ""
            urgency = ""
            
            parts = stored_data.split("|")
            for part in parts:
                if part.startswith("ISSUE_TYPE:"):
                    issue_type = part.replace("ISSUE_TYPE:", "")
                elif part.startswith("DETAILS:"):
                    issue_details = part.replace("DETAILS:", "")
                elif part.startswith("TECH:"):
                    technical_info = part.replace("TECH:", "")
                elif part.startswith("URGENCY:"):
                    urgency = part.replace("URGENCY:", "")
            
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            conversation.guest_name = user_email  # Store email for admin reference
            await conversation.save()
            
            # Send bug report to admin
            try:
                bug_report_data = {
                    "issue_type": issue_type,
                    "issue_details": issue_details,
                    "technical_info": technical_info or "Not applicable",
                    "urgency": urgency,
                    "reporter_email": user_email,
                    "session_id": conversation.session_id,
                    "reported_at": datetime.now(timezone.utc).isoformat()
                }
                print(f"🐛 Bug report submitted: {bug_report_data}")
                
                # Here you would send email notification to development team
                # await send_bug_report_notification(dev_team_emails, bug_report_data)
                
            except Exception as e:
                print(f"⚠️ Failed to send bug report notification: {e}")
            
            # Create completion message
            completion_message = f"Thank you for reporting this issue! 🛠️ We've received your {urgency.lower()} priority report about '{issue_type}'. Our technical team will investigate and contact you at {user_email} with updates."
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Bug report submitted successfully",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": conversation.current_step + 1,
                        "input_type": "bug_report_submitted",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "report_submitted": True,
                        "bug_report": {
                            "issue_type": issue_type,
                            "urgency": urgency,
                            "reporter_email": user_email
                        }
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling contact info: {e}")
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