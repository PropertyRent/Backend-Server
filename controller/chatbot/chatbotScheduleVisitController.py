from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone, date, time
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus
from model.propertyModel import Property
from model.scheduleMeetingModel import ScheduleMeeting, MeetingStatus


class ChatbotScheduleVisitController:
    """Controller for chatbot schedule visit flow with property search"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle schedule visit flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle initial flow setup - when user just selected "Schedule a property visit"
            if "hi! i'm your property assistant" in question_text or conversation.current_step == 0:
                return await ChatbotScheduleVisitController._start_schedule_visit_flow(conversation)
            
            # Step 1: Which property would you like to visit? (keyword search)
            if "which property would you like to visit" in question_text:
                return await ChatbotScheduleVisitController._handle_property_search(conversation, user_response)
            
            # Step 2: Property selection from search results
            elif "please select a property to visit" in question_text or "select a property from the results" in question_text:
                return await ChatbotScheduleVisitController._handle_property_selection(conversation, user_response)
            
            # Step 3: What's your preferred date?
            elif "what's your preferred date" in question_text:
                return await ChatbotScheduleVisitController._handle_date_selection(conversation, user_response)
            
            # Step 4: What time works best for you?
            elif "what time works best for you" in question_text:
                return await ChatbotScheduleVisitController._handle_time_selection(conversation, user_response)
            
            # Step 5: What's your full name?
            elif "what's your full name" in question_text:
                return await ChatbotScheduleVisitController._handle_name_input(conversation, user_response)
            
            # Step 6: What's your contact number?
            elif "what's your contact number" in question_text:
                return await ChatbotScheduleVisitController._handle_phone_input(conversation, user_response)
            
            # Step 7: What's your email address?
            elif "what's your email address" in question_text:
                return await ChatbotScheduleVisitController._handle_email_input(conversation, user_response)
            
            # Default: Move to next step
            return await ChatbotScheduleVisitController._handle_default_flow(conversation, user_response)
            
        except Exception as e:
            print(f"❌ Error in chatbot schedule visit flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _start_schedule_visit_flow(conversation: ChatbotConversation):
        """Start the schedule visit flow"""
        try:
            next_step = conversation.current_step + 1
            property_question = "Which property would you like to visit? Please provide the property name or keywords:"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=property_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Starting property visit scheduling",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": property_question,
                        "step_number": next_step,
                        "input_type": "text",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "placeholder": "Enter property name or keywords"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error starting schedule visit flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _handle_property_search(conversation: ChatbotConversation, user_response: str):
        """Handle property search by keyword"""
        try:
            search_results = await ChatbotScheduleVisitController._search_properties_by_keyword(user_response)
            
            if search_results:
                next_step = conversation.current_step + 1
                search_question = f"I found {len(search_results)} properties matching '{user_response}'. Please select a property to visit:"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=search_question
                )
                
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Property search results found",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": search_question,
                            "properties": search_results,
                            "step_number": next_step,
                            "input_type": "property_selection",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "search_keyword": user_response
                        }
                    }
                )
            else:
                # No properties found
                next_step = conversation.current_step + 1
                no_results_question = f"Sorry, I couldn't find any properties matching '{user_response}'. Could you try with different keywords or contact our support team?"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=no_results_question
                )
                
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "No properties found",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": no_results_question,
                            "step_number": next_step,
                            "input_type": "no_results",
                            "is_final": True,
                            "flow_type": conversation.flow_type,
                            "options": ["Contact Support", "Try Different Keywords"]
                        }
                    }
                )
                
        except Exception as e:
            print(f"❌ Error handling property search: {e}")
            raise

    @staticmethod
    async def _handle_property_selection(conversation: ChatbotConversation, user_response: str):
        """Handle property selection from search results"""
        try:
            # Store selected property ID
            conversation.guest_email = user_response  # Store property ID temporarily
            conversation.current_step += 1
            await conversation.save()
            
            # Move to date selection
            next_step = conversation.current_step + 1
            date_question = "What's your preferred date for the visit?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=date_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Property selected, asking for preferred date",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": date_question,
                        "step_number": next_step,
                        "input_type": "date",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "selected_property_id": user_response,
                        "placeholder": "Select your preferred date"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling property selection: {e}")
            raise

    @staticmethod
    async def _handle_date_selection(conversation: ChatbotConversation, user_response: str):
        """Handle preferred date selection"""
        try:
            # Store date in guest_name field temporarily (we'll reorganize later)
            conversation.guest_name = f"DATE:{user_response}"
            
            next_step = conversation.current_step + 1
            time_question = "What time works best for you?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=time_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Date selected, asking for preferred time",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": time_question,
                        "options": ["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)"],
                        "step_number": next_step,
                        "input_type": "choice",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "selected_property_id": conversation.guest_email,
                        "selected_date": user_response
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling date selection: {e}")
            raise

    @staticmethod
    async def _handle_time_selection(conversation: ChatbotConversation, user_response: str):
        """Handle time selection"""
        try:
            # Get stored date and combine with time
            stored_data = conversation.guest_name or ""
            conversation.guest_name = f"{stored_data}|TIME:{user_response}"
            
            next_step = conversation.current_step + 1
            name_question = "What's your full name?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=name_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Time selected, asking for full name",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": name_question,
                        "step_number": next_step,
                        "input_type": "text",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "selected_property_id": conversation.guest_email,
                        "selected_date": conversation.guest_name.split("DATE:")[1].split("|")[0] if "DATE:" in conversation.guest_name else "Not specified",
                        "selected_time": user_response,
                        "placeholder": "Enter your full name"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling time selection: {e}")
            raise

    @staticmethod
    async def _handle_name_input(conversation: ChatbotConversation, user_response: str):
        """Handle full name input"""
        try:
            # Get stored date/time data and append name
            stored_data = conversation.guest_name or ""
            conversation.guest_name = f"{stored_data}|NAME:{user_response}"
            
            next_step = conversation.current_step + 1
            phone_question = "What's your contact number?"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=phone_question
            )
            
            conversation.current_step = next_step
            await conversation.save()
            
            # Extract date and time from stored data for response
            stored_data_with_name = conversation.guest_name
            date_str = ""
            time_str = ""
            
            if stored_data_with_name:
                parts = stored_data_with_name.split("|")
                for part in parts:
                    if part.startswith("DATE:"):
                        date_str = part.replace("DATE:", "")
                    elif part.startswith("TIME:"):
                        time_str = part.replace("TIME:", "")
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Name received, asking for contact number",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": phone_question,
                        "step_number": next_step,
                        "input_type": "phone",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "selected_property_id": conversation.guest_email,
                        "visitor_name": user_response,
                        "selected_date": date_str,
                        "selected_time": time_str,
                        "placeholder": "Enter your phone number"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling name input: {e}")
            raise

    @staticmethod
    async def _handle_phone_input(conversation: ChatbotConversation, user_response: str):
        """Handle contact number input"""
        try:
            # Append phone to stored data
            stored_data = conversation.guest_name or ""
            conversation.guest_name = f"{stored_data}|PHONE:{user_response}"
            
            next_step = conversation.current_step + 1
            email_question = "What's your email address?"
            
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
                    "message": "Phone number received, asking for email",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": email_question,
                        "step_number": next_step,
                        "input_type": "email",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "selected_property_id": conversation.guest_email,
                        "visitor_name": conversation.guest_name.split("NAME:")[1].split("|")[0] if "NAME:" in conversation.guest_name else "Not specified",
                        "visitor_phone": user_response,
                        "selected_date": conversation.guest_name.split("DATE:")[1].split("|")[0] if "DATE:" in conversation.guest_name else "Not specified",
                        "selected_time": conversation.guest_name.split("TIME:")[1].split("|")[0] if "TIME:" in conversation.guest_name else "Not specified",
                        "placeholder": "Enter your email address"
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling phone input: {e}")
            raise

    @staticmethod
    async def _handle_email_input(conversation: ChatbotConversation, user_response: str):
        """Handle email input and complete the meeting scheduling"""
        try:
            # Get all stored data
            property_id = conversation.guest_email  # This was property ID
            visitor_email = user_response
            
            # Parse stored data from guest_name field
            stored_data = conversation.guest_name or ""
            date_str = ""
            time_str = ""
            visitor_name = ""
            visitor_phone = ""
            
            # Parse the pipe-separated data
            parts = stored_data.split("|")
            for part in parts:
                if part.startswith("DATE:"):
                    date_str = part.replace("DATE:", "")
                elif part.startswith("TIME:"):
                    time_str = part.replace("TIME:", "")
                elif part.startswith("NAME:"):
                    visitor_name = part.replace("NAME:", "")
                elif part.startswith("PHONE:"):
                    visitor_phone = part.replace("PHONE:", "")
            
            # Create meeting record
            try:
                # Parse date (assuming format YYYY-MM-DD or similar)
                meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
                
                # Parse time based on selection
                if "morning" in time_str.lower():
                    meeting_time = time(10, 0)  # 10:00 AM
                elif "afternoon" in time_str.lower():
                    meeting_time = time(14, 0)  # 2:00 PM
                elif "evening" in time_str.lower():
                    meeting_time = time(17, 0)  # 5:00 PM
                else:
                    meeting_time = time(10, 0)  # Default to 10:00 AM
                
                # Get property object
                property_obj = await Property.get_or_none(id=property_id)
                if property_obj:
                    # Create meeting record
                    meeting = await ScheduleMeeting.create(
                        full_name=visitor_name,
                        email=visitor_email,
                        phone=visitor_phone,
                        meeting_date=meeting_date,
                        meeting_time=meeting_time,
                        property=property_obj,
                        message=f"Meeting scheduled via chatbot. Original request: Date: {date_str}, Time: {time_str}",
                        status=MeetingStatus.PENDING
                    )
                    
                    print(f"📅 Meeting created: {meeting.id} for property {property_obj.title}")
                    
                else:
                    print(f"⚠️ Property not found: {property_id}")
                    
            except Exception as e:
                print(f"⚠️ Error creating meeting record: {e}")
            
            # Complete conversation
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Send notification to admin
            try:
                meeting_data = {
                    "property_id": property_id,
                    "visitor_name": visitor_name,
                    "visitor_email": visitor_email,
                    "visitor_phone": visitor_phone,
                    "preferred_date": date_str,
                    "preferred_time": time_str,
                    "session_id": conversation.session_id
                }
                print(f"📧 Meeting scheduled - Admin notification: {meeting_data}")
            except Exception as e:
                print(f"⚠️ Failed to send admin notification: {e}")
            
            # Create completion message
            completion_message = f"Thank you {visitor_name}! 🎉 Your property visit has been scheduled. Our team will contact you at {visitor_phone} or {visitor_email} to confirm the details shortly."
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Property visit scheduled successfully",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": completion_message,
                        "step_number": conversation.current_step + 1,
                        "input_type": "visit_scheduled",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "visit_scheduled": True,
                        "meeting_details": {
                            "property_id": property_id,
                            "visitor_name": visitor_name,
                            "visitor_email": visitor_email,
                            "visitor_phone": visitor_phone,
                            "preferred_date": date_str,
                            "preferred_time": time_str
                        }
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error handling email input: {e}")
            raise

    @staticmethod
    async def _search_properties_by_keyword(keyword: str) -> List[Dict]:
        """Search properties by keyword"""
        try:
            # Search properties by title, description, city, or address
            properties = await Property.filter(
                title__icontains=keyword
            ).limit(10)
            
            if not properties:
                # Try searching by city
                properties = await Property.filter(
                    city__icontains=keyword
                ).limit(10)
            
            if not properties:
                # Try searching by address
                properties = await Property.filter(
                    address__icontains=keyword
                ).limit(10)
            
            search_results = []
            for prop in properties:
                search_results.append({
                    "id": str(prop.id),
                    "title": prop.title,
                    "address": prop.address or "Address not specified",
                    "city": prop.city or "City not specified",
                    "price": f"₹{prop.price:,}/month" if prop.price else "Price on request",
                    "property_type": prop.property_type or "Not specified",
                    "description": prop.description[:100] + "..." if prop.description and len(prop.description) > 100 else prop.description or "No description available"
                })
            
            return search_results
            
        except Exception as e:
            print(f"❌ Error searching properties by keyword: {e}")
            return []

    @staticmethod
    async def _handle_default_flow(conversation: ChatbotConversation, user_response: str):
        """Handle default flow when no specific question matches"""
        try:
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)
        except Exception as e:
            print(f"❌ Error in default flow: {e}")
            raise