from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus
from model.propertyModel import Property


class RentInquiryController:
    """Controller for rent inquiry flow - 'Ask about a specific property'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle rent inquiry flow responses"""
        try:
            question_text = current_message.question_text.lower()
            
            # Handle initial flow setup - when user just selected "Ask about a specific property"
            if "hi! i'm your property assistant" in question_text or conversation.current_step == 0:
                return await RentInquiryController._start_rent_inquiry_flow(conversation)
            
            # Handle special cases for satisfaction responses
            if current_message.question_text.startswith("Great! I found") and "properties matching" in current_message.question_text:
                return await RentInquiryController._handle_satisfaction_response(conversation, user_response)
            elif "Sorry, I couldn't find any properties" in current_message.question_text:
                return await RentInquiryController._handle_satisfaction_response(conversation, user_response)
            
            # Step 1: Do you have a specific property in mind?
            if "do you have a specific property in mind" in question_text:
                return await RentInquiryController._handle_property_mind_question(conversation, user_response)
            
            # Step 1.5: Handle property name/keyword search
            elif "please provide the property name or keyword" in question_text:
                return await RentInquiryController._handle_keyword_search(conversation, user_response)
            
            # Step 2: Handle property selection from search results or browse
            elif ("i found" in question_text and "properties matching" in question_text) or \
                 ("here are some available properties" in question_text) or \
                 ("sorry, i couldn't find any properties matching" in question_text):
                return await RentInquiryController._handle_property_selection(conversation, user_response)
            
            # Step 2: Which property would you like to know about?
            elif "which property would you like to know about" in question_text:
                return await RentInquiryController._handle_property_selection(conversation, user_response)
            
            # Step 3: What's your preferred contact method?
            elif "what's your preferred contact method" in question_text:
                return await RentInquiryController._handle_contact_method_selection(conversation, user_response)
            
            # Step 4: Handle contact details submission
            elif current_message.question_text.lower().startswith("please provide your"):
                return await RentInquiryController._handle_contact_details_submission(conversation, user_response)
            
            # Step 3: What specific information do you need?
            elif "what specific information do you need" in question_text:
                return await RentInquiryController._handle_information_request(conversation, user_response, question_text)
            
            # Default: Move to next step or satisfaction
            return await RentInquiryController._handle_default_flow(conversation, user_response)
            
        except Exception as e:
            print(f"❌ Error in rent inquiry flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _start_rent_inquiry_flow(conversation: ChatbotConversation):
        """Start the rent inquiry flow"""
        try:
            # Start with the property mind question
            next_step = conversation.current_step + 1
            property_question = "Do you have a specific property in mind?"
            
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
                    "message": "Starting property inquiry flow",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": property_question,
                        "step_number": next_step,
                        "input_type": "yes_no_question",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "options": ["Yes", "No"]
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error starting rent inquiry flow: {e}")
            from .conversationController import ConversationController
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _handle_property_mind_question(conversation: ChatbotConversation, user_response: str):
        """Handle 'Do you have a specific property in mind?' question"""
        try:
            if user_response.lower() == "yes":
                # User has specific property in mind - ask for property name/keyword
                next_step = conversation.current_step + 1
                name_question = "Please provide the property name or keyword you're looking for:"
                
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
                        "message": "Please provide property name or keyword",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": name_question,
                            "step_number": next_step,
                            "input_type": "text",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "placeholder": "Enter property name or keyword..."
                        }
                    }
                )
            
            elif user_response.lower() == "no":
                # User doesn't have specific property - show available properties
                next_step = conversation.current_step + 1
                property_choices = await RentInquiryController._get_property_titles_for_choice()
                
                if property_choices:
                    browse_question = "Here are some available properties you might be interested in:"
                    
                    await ChatbotMessage.create(
                        conversation=conversation,
                        step_number=next_step,
                        question_text=browse_question
                    )
                    
                    conversation.current_step = next_step
                    await conversation.save()
                    
                    return JSONResponse(
                        status_code=HTTP_200_OK,
                        content={
                            "success": True,
                            "message": "Showing available properties",
                            "data": {
                                "session_id": conversation.session_id,
                                "question": browse_question,
                                "properties": property_choices,
                                "step_number": next_step,
                                "input_type": "property_browse",
                                "is_final": False,
                                "flow_type": conversation.flow_type,
                                "additional_options": [
                                    {
                                        "value": "proceed_next",
                                        "label": "Proceed Next",
                                        "description": "Skip property selection and continue with general inquiry"
                                    }
                                ]
                            }
                        }
                    )
                else:
                    # No properties available
                    return JSONResponse(
                        status_code=HTTP_200_OK,
                        content={
                            "success": True,
                            "message": "No properties available",
                            "data": {
                                "session_id": conversation.session_id,
                                "question": "Sorry, we don't have any properties available at the moment. Please contact our team directly.",
                                "step_number": next_step,
                                "input_type": "no_properties",
                                "is_final": True,
                                "flow_type": conversation.flow_type,
                                "options": ["Yes, I'm satisfied", "No, I need more help"]
                            }
                        }
                    )
        except Exception as e:
            print(f"❌ Error handling property mind question: {e}")
            raise

    @staticmethod
    async def _handle_keyword_search(conversation: ChatbotConversation, user_response: str):
        """Handle property keyword search"""
        try:
            search_results = await RentInquiryController._search_properties_by_keyword(user_response)
            
            if search_results:
                next_step = conversation.current_step + 1
                search_question = f"I found {len(search_results)} properties matching '{user_response}'. Please select one:"
                
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
                            "input_type": "property_search_results",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "search_keyword": user_response,
                            "additional_options": [
                                {
                                    "value": "proceed_next",
                                    "label": "Proceed Next",
                                    "description": "Skip property selection and continue with general inquiry"
                                }
                            ]
                        }
                    }
                )
            else:
                # No properties found with the keyword
                next_step = conversation.current_step + 1
                no_results_question = f"Sorry, I couldn't find any properties matching '{user_response}'. Here are some available properties you might like:"
                
                # Show available properties instead
                available_properties = await RentInquiryController._get_property_titles_for_choice()
                
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
                        "message": "No search results, showing available properties",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": no_results_question,
                            "properties": available_properties,
                            "step_number": next_step,
                            "input_type": "property_search_no_results",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "search_keyword": user_response,
                            "additional_options": [
                                {
                                    "value": "proceed_next",
                                    "label": "Proceed Next",
                                    "description": "Skip property selection and continue with general inquiry"
                                }
                            ]
                        }
                    }
                )
        except Exception as e:
            print(f"❌ Error handling keyword search: {e}")
            raise

    @staticmethod
    async def _handle_property_selection(conversation: ChatbotConversation, user_response: str):
        """Handle property selection from search results or browse"""
        try:
            # Check if user selected "Proceed Next" option (multiple possible formats)
            skip_options = [
                "proceed next", 
                "proceed_next",
                "skip property selection and continue with general inquiry",
                "skip property selection",
                "continue with general inquiry"
            ]
            if user_response.lower() in skip_options:
                # User wants to skip property selection - ask for email for general updates
                next_step = conversation.current_step + 1
                email_question = "Please provide your email address so we can notify you when we have properties matching your preferences:"
                
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=next_step,
                    question_text=email_question
                )
                
                # Mark this as a general inquiry (no specific property)
                conversation.guest_email = "GENERAL_INQUIRY"  # Mark as general inquiry
                conversation.current_step = next_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Asking for email for general property updates",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": email_question,
                            "step_number": next_step,
                            "input_type": "email",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "inquiry_type": "general",
                            "selected_property_id": None,
                            "placeholder": "Enter your email address",
                            "show_send_button": True
                        }
                    }
                )
            else:
                # User selected a specific property - store selected property ID and move to contact method
                conversation.guest_email = user_response  # Temporarily store property ID
                conversation.current_step += 1
                await conversation.save()
                
                # Move to contact method question directly
                next_step = conversation.current_step + 1
                contact_question = "What's your preferred contact method?"
                
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
                        "message": "Property selected, asking for contact method",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": contact_question,
                            "options": ["Email", "Phone", "WhatsApp"],
                            "step_number": next_step,
                            "input_type": "choice",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "selected_property_id": user_response
                        }
                    }
                )
        except Exception as e:
            print(f"❌ Error handling property selection: {e}")
            raise

    @staticmethod
    async def _handle_contact_method_selection(conversation: ChatbotConversation, user_response: str):
        """Handle contact method selection"""
        try:
            contact_method = user_response.lower()
            next_step = conversation.current_step + 1
            
            if contact_method == "email":
                contact_field_question = "Please provide your email address:"
                input_type = "email"
                placeholder = "Enter your email address"
            elif contact_method == "phone":
                contact_field_question = "Please provide your phone number:"
                input_type = "phone"
                placeholder = "Enter your phone number"
            elif contact_method == "whatsapp":
                contact_field_question = "Please provide your WhatsApp number:"
                input_type = "phone"
                placeholder = "Enter your WhatsApp number"
            else:
                contact_field_question = "Please provide your contact information:"
                input_type = "text"
                placeholder = "Enter your contact details"
            
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=next_step,
                question_text=contact_field_question
            )
            
            # Store contact method preference
            conversation.guest_name = contact_method  # Store contact method temporarily
            conversation.current_step = next_step
            await conversation.save()
            
            # Get the stored property ID
            selected_property_id = conversation.guest_email  # Property ID stored here
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Contact method selected, asking for details",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": contact_field_question,
                        "step_number": next_step,
                        "input_type": input_type,
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "contact_method": contact_method,
                        "placeholder": placeholder,
                        "show_send_button": True,
                        "selected_property_id": selected_property_id
                    }
                }
            )
        except Exception as e:
            print(f"❌ Error handling contact method selection: {e}")
            raise

    @staticmethod
    async def _handle_contact_details_submission(conversation: ChatbotConversation, user_response: str):
        """Handle contact details submission"""
        try:
            contact_method = conversation.guest_name or "contact method"  # Get stored contact method
            selected_property_id = conversation.guest_email  # Get stored property ID before overwriting
            
            # Store contact details (we'll use guest_phone to store actual contact details to preserve property ID)
            conversation.guest_phone = user_response  # Store actual contact details here
            conversation.current_step += 1
            
            conversation.status = ConversationStatus.COMPLETED
            conversation.completed_at = datetime.now(timezone.utc)
            await conversation.save()
            
            # Check if this is a general inquiry or specific property inquiry
            is_general_inquiry = selected_property_id == "GENERAL_INQUIRY"
            
            # Send contact details to admin (you can implement email/notification here)
            try:
                contact_info = {
                    "property_id": selected_property_id if not is_general_inquiry else None,
                    "contact_method": contact_method,
                    "contact_value": user_response,
                    "session_id": conversation.session_id,
                    "inquiry_type": "general" if is_general_inquiry else "specific_property",
                    "selected_property": selected_property_id if not is_general_inquiry else None
                }
                print(f"📧 Contact details received: {contact_info}")
            except Exception as e:
                print(f"⚠️ Failed to process contact details: {e}")
            
            # Customize thank you message based on inquiry type
            if is_general_inquiry:
                thank_you_message = "Thank you! 🎉 We've received your email address. We will reach out to you when we have property matching you."
                success_message = "Email received for general property updates"
            else:
                thank_you_message = f"Thank you! 🎉 We've received your {contact_method} details. Our team will contact you soon regarding your property inquiry."
                success_message = "Your inquiry has been submitted"
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": success_message,
                    "data": {
                        "session_id": conversation.session_id,
                        "question": thank_you_message,
                        "step_number": conversation.current_step,
                        "input_type": "thank_you_message",
                        "is_final": True,
                        "flow_type": conversation.flow_type,
                        "conversation_completed": True,
                        "contact_submitted": True,
                        "inquiry_type": "general" if is_general_inquiry else "specific_property",
                        "selected_property_id": None if is_general_inquiry else selected_property_id,
                        "contact_details": {
                            "method": "email" if is_general_inquiry else contact_method,
                            "value": user_response
                        }
                    }
                }
            )
        except Exception as e:
            print(f"❌ Error handling contact details submission: {e}")
            raise

    @staticmethod
    async def _handle_information_request(conversation: ChatbotConversation, user_response: str, question_text: str):
        """Handle specific information requests"""
        try:
            details_message = ""
            
            if "about our properties in general" in question_text:
                # Handle general information requests
                if user_response.lower() == "general rent pricing":
                    details_message = "💰 **General Rent Pricing Information:**\n"
                    details_message += "• Studio/1 BHK: ₹15,000 - ₹35,000/month\n"
                    details_message += "• 2 BHK: ₹25,000 - ₹55,000/month\n"
                    details_message += "• 3 BHK: ₹40,000 - ₹80,000/month\n"
                    details_message += "• 4+ BHK: ₹60,000+/month\n"
                    details_message += "• Prices vary by location, amenities, and property condition"
                    
                elif user_response.lower() == "available locations":
                    details_message = "📍 **Available Locations:**\n"
                    details_message += "• New York, NY - Multiple properties\n"
                    details_message += "• Downtown areas with easy transport access\n"
                    details_message += "• Suburban locations with parking facilities\n"
                    details_message += "• Near schools, hospitals, and shopping centers"
                    
                elif user_response.lower() == "property types available":
                    details_message = "🏠 **Property Types Available:**\n"
                    details_message += "• Modern Downtown Apartments\n"
                    details_message += "• Suburban Houses\n"
                    details_message += "• Studio Apartments\n"
                    details_message += "• Luxury Villas\n"
                    details_message += "• Furnished and unfurnished options available"
                    
                elif user_response.lower() == "application process":
                    details_message = "📋 **Application Process:**\n"
                    details_message += "• Step 1: Submit online application with required documents\n"
                    details_message += "• Step 2: Background and credit verification\n"
                    details_message += "• Step 3: Property viewing and inspection\n"
                    details_message += "• Step 4: Lease agreement signing\n"
                    details_message += "• Step 5: Security deposit and first month rent payment\n"
                    details_message += "• Processing time: 3-7 business days"
                    
                elif user_response.lower() == "document requirements":
                    details_message = "📄 **General Document Requirements:**\n"
                    details_message += "• Valid Government ID (Aadhaar/PAN/Passport)\n"
                    details_message += "• Income proof (Salary slips/ITR)\n"
                    details_message += "• Bank statements (last 3 months)\n"
                    details_message += "• Employment verification letter\n"
                    details_message += "• Previous landlord reference (if applicable)\n"
                    details_message += "• Passport size photographs\n"
                    details_message += "• Additional documents may be required based on property"
                    
                elif user_response.lower() == "contact support":
                    details_message = "📞 **Contact Support:**\n"
                    details_message += "• Email: support@propertyrent.com\n"
                    details_message += "• Phone: +1-234-567-8900\n"
                    details_message += "• WhatsApp: +1-234-567-8900\n"
                    details_message += "• Office Hours: Mon-Fri 9 AM - 6 PM\n"
                    details_message += "• Emergency Support: Available 24/7"
            else:
                # Handle specific property information requests
                property_id = conversation.guest_email  # Retrieved stored property ID
                property_details = await RentInquiryController._get_property_details(property_id, user_response)
                
                if "error" in property_details:
                    details_message = "Sorry, I couldn't retrieve the property details. Please contact our team for assistance."
                else:
                    # Format details message based on info type
                    if user_response.lower() == "rent details":
                        details_message = f"💰 **Rent Details for {property_details['title']}:**\n"
                        details_message += f"• Monthly Rent: {property_details.get('rent', 'Contact for pricing')}\n"
                        details_message += f"• Security Deposit: {property_details.get('deposit', 'Contact for deposit info')}\n"
                        details_message += f"• Application Fee: {property_details.get('application_fee', 'No fee')}\n"
                        details_message += f"• Lease Term: {property_details.get('lease_term', 'Contact for terms')}"
                        
                    elif user_response.lower() == "amenities":
                        details_message = f"🏠 **Amenities for {property_details['title']}:**\n"
                        amenities = property_details.get('amenities', [])
                        if amenities:
                            details_message += "• " + "\n• ".join(amenities)
                        else:
                            details_message += "Contact our team for detailed amenity information."
                            
                    elif user_response.lower() == "location info":
                        details_message = f"📍 **Location Details for {property_details['title']}:**\n"
                        details_message += f"• Address: {property_details.get('address', 'Contact for address')}\n"
                        details_message += f"• City: {property_details.get('city', 'Not specified')}\n"
                        details_message += f"• State: {property_details.get('state', 'Not specified')}\n"
                        details_message += f"• Pincode: {property_details.get('pincode', 'Contact for pincode')}"
                        
                    elif user_response.lower() == "availability":
                        details_message = f"📅 **Availability for {property_details['title']}:**\n"
                        details_message += f"• Available From: {property_details.get('available_from', 'Contact for availability')}\n"
                        details_message += f"• Current Status: {property_details.get('status', 'Contact for status')}"
                        
                    elif user_response.lower() == "documents needed":
                        details_message = f"📄 **Documents Required for {property_details['title']}:**\n"
                        docs = property_details.get('documents', [])
                        if docs:
                            details_message += "• " + "\n• ".join(docs)
                        details_message += f"\n\n{property_details.get('additional_info', '')}"
            
            # Create response with information
            details_step = conversation.current_step + 1
            await ChatbotMessage.create(
                conversation=conversation,
                step_number=details_step,
                question_text=details_message
            )
            
            conversation.current_step += 1
            await conversation.save()
            
            # Get the stored property ID
            selected_property_id = conversation.guest_email  # Property ID stored here
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Information provided",
                    "data": {
                        "session_id": conversation.session_id,
                        "question": details_message,
                        "step_number": details_step,
                        "input_type": "info_response",
                        "is_final": False,
                        "flow_type": conversation.flow_type,
                        "options": ["Yes, I'm satisfied", "No, I need more help"],
                        "selected_property_id": selected_property_id
                    }
                }
            )
        except Exception as e:
            print(f"❌ Error handling information request: {e}")
            raise

    @staticmethod
    async def _handle_satisfaction_response(conversation: ChatbotConversation, user_response: str):
        """Handle satisfaction response for search results"""
        try:
            is_satisfied = user_response.lower() == "yes, i'm satisfied"
            
            if is_satisfied:
                # User is satisfied - show thank you message and complete conversation
                selected_property_id = conversation.guest_email  # Get stored property ID
                
                conversation.is_satisfied = True
                conversation.status = ConversationStatus.COMPLETED
                conversation.completed_at = datetime.now(timezone.utc)
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Thank you for the journey! 🎉",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": "Thank you for using our property assistant! We're glad we could help you find what you were looking for. Have a great day! 😊",
                            "conversation_completed": True,
                            "escalated": False,
                            "restart": False,
                            "input_type": "completion",
                            "is_final": True,
                            "flow_type": conversation.flow_type,
                            "selected_property_id": selected_property_id
                        }
                    }
                )
            else:
                # User needs more help - restart conversation from step 1
                conversation.is_satisfied = False
                conversation.status = ConversationStatus.ACTIVE
                conversation.flow_type = None  # Reset flow type
                conversation.current_step = 0  # Reset to initial step
                await conversation.save()
                
                # Get initial question again
                from .chatbotEngine import ChatbotFlowEngine
                initial_question = ChatbotFlowEngine.get_initial_question()
                
                # Create new initial message
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=0,
                    question_text=initial_question["question"]
                )
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Let's start over! I'm here to help you.",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": initial_question["question"],
                            "options": initial_question["options"],
                            "step_number": initial_question["step_number"],
                            "input_type": initial_question["input_type"],
                            "is_final": initial_question["is_final"],
                            "flow_type": None,
                            "restart": True
                        }
                    }
                )
        except Exception as e:
            print(f"❌ Error handling satisfaction response: {e}")
            raise

    @staticmethod
    async def _handle_default_flow(conversation: ChatbotConversation, user_response: str):
        """Handle default flow continuation"""
        from .conversationController import ConversationController
        return await ConversationController.handle_satisfaction_question(conversation)

    # Helper methods
    @staticmethod
    async def _get_property_titles_for_choice() -> List[Dict]:
        """Get 6-7 property titles for user to choose from"""
        try:
            # Get active properties with basic info
            properties = await Property.all().limit(7)
            
            property_choices = []
            for prop in properties:
                property_choices.append({
                    "id": str(prop.id),
                    "title": prop.title,
                    "location": f"{prop.city}, {prop.state}" if prop.city and prop.state else "Location not specified",
                    "price": f"₹{prop.price:,}/month" if prop.price else "Price not available"
                })
            
            return property_choices
            
        except Exception as e:
            print(f"❌ Error getting property titles: {e}")
            return []

    @staticmethod
    async def _search_properties_by_keyword(keyword: str) -> List[Dict]:
        """Search properties by title or keyword"""
        try:
            # Search properties by title containing the keyword (case-insensitive)
            properties = await Property.filter(
                title__icontains=keyword
            ).limit(10)
            
            # If no results found by title, try searching in description or other fields
            if not properties:
                properties = await Property.filter(
                    description__icontains=keyword
                ).limit(10)
            
            # If still no results, try searching by city or location
            if not properties:
                properties = await Property.filter(
                    city__icontains=keyword
                ).limit(10)
            
            search_results = []
            for prop in properties:
                search_results.append({
                    "id": str(prop.id),
                    "title": prop.title,
                    "location": f"{prop.city}, {prop.state}" if prop.city and prop.state else "Location not specified",
                    "price": f"₹{prop.price:,}/month" if prop.price else "Price not available",
                    "description": prop.description[:100] + "..." if prop.description and len(prop.description) > 100 else prop.description
                })
            
            print(f"🔍 Found {len(search_results)} properties for keyword: {keyword}")
            return search_results
            
        except Exception as e:
            print(f"❌ Error searching properties by keyword: {e}")
            return []

    @staticmethod
    async def _get_property_details(property_id: str, info_type: str) -> Dict:
        """Get specific property details based on information type requested"""
        try:
            property_obj = await Property.get_or_none(id=property_id)
            if not property_obj:
                return {"error": "Property not found"}
            
            details = {
                "property_id": str(property_obj.id),
                "title": property_obj.title,
                "basic_info": f"{property_obj.title} - {property_obj.city}, {property_obj.state}"
            }
            
            if info_type.lower() == "rent details":
                details.update({
                    "rent": f"₹{property_obj.price:,}/month" if property_obj.price else "Price not available",
                    "deposit": f"₹{property_obj.deposit:,}" if property_obj.deposit else "Deposit info not available",
                    "application_fee": f"₹{property_obj.application_fee}" if property_obj.application_fee else "No application fee",
                    "lease_term": property_obj.lease_term or "Contact for lease terms"
                })
                
            elif info_type.lower() == "amenities":
                amenities = property_obj.amenities if property_obj.amenities else []
                details.update({
                    "amenities": amenities if amenities else ["Contact for amenity details"],
                    "appliances": property_obj.appliances_included if property_obj.appliances_included else ["Contact for appliance details"]
                })
                
            elif info_type.lower() == "location info":
                details.update({
                    "address": property_obj.address or "Contact for full address",
                    "city": property_obj.city or "Not specified",
                    "state": property_obj.state or "Not specified",
                    "pincode": property_obj.pincode or "Contact for pincode",
                    "coordinates": f"Lat: {property_obj.latitude}, Long: {property_obj.longitude}" if property_obj.latitude and property_obj.longitude else "Coordinates not available"
                })
                
            elif info_type.lower() == "availability":
                details.update({
                    "available_from": property_obj.available_from.strftime('%Y-%m-%d') if property_obj.available_from else "Contact for availability",
                    "status": property_obj.status or "Contact for current status"
                })
                
            elif info_type.lower() == "documents needed":
                details.update({
                    "documents": [
                        "Valid Government ID (Aadhaar/PAN/Passport)",
                        "Income proof (Salary slips/ITR)",
                        "Bank statements (last 3 months)",
                        "Employment verification letter",
                        "Previous landlord reference (if applicable)",
                        "Passport size photographs"
                    ],
                    "additional_info": "Specific requirements may vary. Contact our team for detailed document checklist."
                })
            
            return details
            
        except Exception as e:
            print(f"❌ Error getting property details: {e}")
            return {"error": f"Failed to get property details: {str(e)}"}