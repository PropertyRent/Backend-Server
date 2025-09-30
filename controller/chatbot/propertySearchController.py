from fastapi.responses import JSONResponse
from starlette.status import *
from datetime import datetime, timezone
from typing import Dict, List
from model.chatbotModel import ChatbotConversation, ChatbotMessage, ConversationStatus
from model.propertyModel import Property
from .conversationController import ConversationController


class PropertySearchController:
    """Controller for property search flow - 'Find a property to rent'"""
    
    @staticmethod
    async def handle_response(conversation: ChatbotConversation, current_message: ChatbotMessage, user_response: str):
        """Handle property search flow responses"""
        try:
            # Check if this is the end of property search flow
            flow_questions = [
                "what type of property are you looking for",
                "which city are you interested in",
                "what's your budget range per month",
                "how many bedrooms do you need",
                "do you have pets",
                "when do you want to move in",
                "any specific amenities you need"
            ]
            
            current_question = current_message.question_text.lower()
            
            # Check if we've completed all questions
            question_step = conversation.current_step
            
            if question_step >= len(flow_questions):
                # End of flow - search for matching properties
                return await PropertySearchController._search_and_display_properties(conversation)
            
            # Continue with next question
            from .chatbotEngine import ChatbotFlowEngine
            next_question_data = ChatbotFlowEngine.get_next_question(conversation.flow_type, question_step)
            
            if not next_question_data:
                # End of flow - search for properties
                return await PropertySearchController._search_and_display_properties(conversation)
            
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
                    "message": "Next property search question",
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
            print(f"❌ Error in property search flow: {e}")
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _search_and_display_properties(conversation: ChatbotConversation):
        """Search for properties based on user criteria and display results"""
        try:
            # Search for matching properties
            matching_properties = await PropertySearchController._search_matching_properties(conversation)
            
            if matching_properties:
                # Show search results
                search_results_step = conversation.current_step + 1
                property_list = []
                for prop in matching_properties:
                    property_list.append({
                        "id": str(prop.id),
                        "title": prop.title,
                        "location": f"{prop.city}, {prop.state}" if prop.city and prop.state else "Location not specified",
                        "price": f"₹{prop.price:,}/month" if prop.price else "Price not available",
                        "type": prop.property_type,
                        "bedrooms": prop.bedrooms
                    })
                
                search_results_question = f"Great! I found {len(matching_properties)} properties matching your criteria:"
                
                # Create search results message
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=search_results_step,
                    question_text=search_results_question
                )
                
                conversation.current_step = search_results_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "Search results found",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": search_results_question,
                            "properties": property_list,
                            "step_number": search_results_step,
                            "input_type": "property_results",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "options": ["Yes, I'm satisfied", "No, I need more help"]
                        }
                    }
                )
            else:
                # No properties found
                no_results_step = conversation.current_step + 1
                no_results_question = "Sorry, I couldn't find any properties matching your exact criteria. You can try adjusting your preferences or contact our team for more options."
                
                # Create no results message
                await ChatbotMessage.create(
                    conversation=conversation,
                    step_number=no_results_step,
                    question_text=no_results_question
                )
                
                conversation.current_step = no_results_step
                await conversation.save()
                
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": "No matching properties found",
                        "data": {
                            "session_id": conversation.session_id,
                            "question": no_results_question,
                            "properties": [],
                            "step_number": no_results_step,
                            "input_type": "no_results",
                            "is_final": False,
                            "flow_type": conversation.flow_type,
                            "options": ["Yes, I'm satisfied", "No, I need more help"]
                        }
                    }
                )
                
        except Exception as e:
            print(f"❌ Error searching properties: {e}")
            return await ConversationController.handle_satisfaction_question(conversation)

    @staticmethod
    async def _search_matching_properties(conversation: ChatbotConversation) -> List[Property]:
        """Search for properties matching user's criteria from conversation responses"""
        try:
            # Get all messages with responses for this conversation
            messages = await ChatbotMessage.filter(
                conversation=conversation,
                user_response__not_isnull=True
            ).order_by('step_number')
            
            # Extract search criteria from responses
            search_criteria = {}
            
            for msg in messages:
                question = msg.question_text.lower()
                response = msg.user_response.lower() if msg.user_response else ""
                
                # Property type
                if "type of property" in question:
                    if response != "any":
                        search_criteria['property_type'] = response.title()
                
                # City
                elif "which city" in question:
                    search_criteria['city'] = response.title()
                
                # Budget range
                elif "budget range" in question:
                    if "under" in response:
                        search_criteria['price__lt'] = 10000
                    elif "10,000-25,000" in response:
                        search_criteria['price__gte'] = 10000
                        search_criteria['price__lte'] = 25000
                    elif "25,000-50,000" in response:
                        search_criteria['price__gte'] = 25000
                        search_criteria['price__lte'] = 50000
                    elif "50,000-1,00,000" in response:
                        search_criteria['price__gte'] = 50000
                        search_criteria['price__lte'] = 100000
                    elif "above" in response:
                        search_criteria['price__gt'] = 100000
                
                # Bedrooms
                elif "how many bedrooms" in question:
                    if "studio" in response or "0" in response:
                        search_criteria['bedrooms'] = 0
                    elif "1 bhk" in response:
                        search_criteria['bedrooms'] = 1
                    elif "2 bhk" in response:
                        search_criteria['bedrooms'] = 2
                    elif "3 bhk" in response:
                        search_criteria['bedrooms'] = 3
                    elif "4+" in response:
                        search_criteria['bedrooms__gte'] = 4
                
                # Pets
                elif "pets" in question:
                    # Store pet preference for filtering
                    search_criteria['_pet_preference'] = response == "yes"
                
                # Amenities
                elif "amenities" in question and response != "none specific":
                    search_criteria['_amenity_preference'] = response
            
            print(f"🔍 Search criteria: {search_criteria}")
            
            # Build query
            query = Property.all()
            
            # Apply filters
            for key, value in search_criteria.items():
                if key.startswith('_'):  # Skip internal preferences
                    continue
                query = query.filter(**{key: value})
            
            # Additional filtering for pets if specified
            if search_criteria.get('_pet_preference') is True:
                # Filter properties that allow pets
                query = query.filter(pet_policy__icontains="allowed")
            
            # Get results (limit to 10 for better UX)
            properties = await query.limit(10)
            
            print(f"✅ Found {len(properties)} matching properties")
            return properties
            
        except Exception as e:
            print(f"❌ Error searching properties: {e}")
            return []