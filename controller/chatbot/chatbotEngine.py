import uuid
from typing import Dict, List, Optional
from model.chatbotModel import ChatbotFlowType


class ChatbotFlowEngine:
    """Chatbot conversation flow engine with predefined questions"""
    
    # Define all conversation flows
    FLOWS = {
        "initial": [
            {
                "question": "Hi! I'm your property assistant. How can I help you today?",
                "options": [
                    "Find a property to rent",
                    "Ask about a specific property", 
                    "Schedule a property visit",
                    "General support",
                    "Report an issue",
                    "Give feedback"
                ],
                "input_type": "choice",
                "next_flow": {
                    "Find a property to rent": "property_search",
                    "Ask about a specific property": "rent_inquiry",
                    "Schedule a property visit": "schedule_visit", 
                    "General support": "general_support",
                    "Report an issue": "bug_report",
                    "Give feedback": "feedback"
                }
            }
        ],
        
        "property_search": [
            {"question": "What type of property are you looking for?", 
             "options": ["Apartment", "House", "Studio", "Villa", "Any"], "input_type": "choice"},
            {"question": "Which city are you interested in?", "input_type": "text"},
            {"question": "What's your budget range per month?",
             "options": ["Under ₹10,000", "₹10,000-₹25,000", "₹25,000-₹50,000", "₹50,000-₹1,00,000", "Above ₹1,00,000"], 
             "input_type": "choice"},
            {"question": "How many bedrooms do you need?", 
             "options": ["Studio/0", "1 BHK", "2 BHK", "3 BHK", "4+ BHK"], "input_type": "choice"},
            {"question": "Do you have pets?", 
             "options": ["Yes", "No"], "input_type": "choice"},
            {"question": "When do you want to move in?", 
             "options": ["Immediately", "Within 1 month", "1-3 months", "3+ months"], "input_type": "choice"},
            {"question": "Any specific amenities you need?", 
             "options": ["Parking", "Gym", "Swimming Pool", "Security", "None specific"], "input_type": "choice"}
        ],
        
        "rent_inquiry": [
            {"question": "Do you have a specific property in mind?", 
             "options": ["Yes", "No"], "input_type": "choice"}
            # Note: This flow uses dynamic questions handled by RentInquiryController
            # Subsequent questions are generated dynamically based on user responses:
            # - Property keyword search (if Yes)
            # - Property selection from search results/browse (dynamic)
            # - Contact method selection (dynamic)
            # - Contact details collection (dynamic)
            # - Information requests (dynamic)
        ],
        
        "schedule_visit": [
            {"question": "Which property would you like to visit?", "input_type": "text"},
            {"question": "What's your preferred date?", "input_type": "date"},
            {"question": "What time works best for you?", 
             "options": ["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)"], 
             "input_type": "choice"},
            {"question": "What's your full name?", "input_type": "text"},
            {"question": "What's your contact number?", "input_type": "phone"},
            {"question": "What's your email address?", "input_type": "email"}
        ],
        
        "general_support": [
            {"question": "What do you need help with?", 
             "options": ["Account issues", "Payment problems", "Property inquiry", "Technical support", "Other"], 
             "input_type": "choice"},
            {"question": "Can you describe your issue briefly?", "input_type": "text"},
            {"question": "How urgent is this matter?", 
             "options": ["Very urgent", "Moderate", "Not urgent"], "input_type": "choice"},
            {"question": "What's the best way to reach you?", 
             "options": ["Email", "Phone", "WhatsApp"], "input_type": "choice"}
        ],
        
        "bug_report": [
            {"question": "What type of issue are you experiencing?", 
             "options": ["Website not loading", "Search not working", "Images not showing", "Form submission error", "Other"], 
             "input_type": "choice"},
            {"question": "On which page did this happen?", "input_type": "text"},
            {"question": "What browser are you using?", 
             "options": ["Chrome", "Firefox", "Safari", "Edge", "Other"], "input_type": "choice"},
            {"question": "Can you describe what happened?", "input_type": "text"},
            {"question": "What's your email for updates?", "input_type": "email"}
        ],
        
        "feedback": [
            {"question": "What would you like to give feedback about?", 
             "options": ["Website design", "Property listings", "Customer service", "Overall experience", "Suggestions"], 
             "input_type": "choice"},
            {"question": "How would you rate your experience? (1-5)", 
             "options": ["1 - Very Poor", "2 - Poor", "3 - Average", "4 - Good", "5 - Excellent"], 
             "input_type": "choice"},
            {"question": "What did you like most?", "input_type": "text"},
            {"question": "What can we improve?", "input_type": "text"},
            {"question": "Would you recommend us to others?", 
             "options": ["Definitely", "Probably", "Not sure", "Probably not", "Definitely not"], 
             "input_type": "choice"}
        ]
    }

    @classmethod
    def get_initial_question(cls) -> Dict:
        """Get the first question to start conversation"""
        initial_flow = cls.FLOWS["initial"][0]
        return {
            "question": initial_flow["question"],
            "options": initial_flow["options"],
            "input_type": initial_flow["input_type"],
            "step_number": 0,
            "is_final": False
        }

    @classmethod
    def get_next_question(cls, flow_type: str, step: int) -> Optional[Dict]:
        """Get next question in the flow"""
        if flow_type not in cls.FLOWS:
            return None
            
        flow = cls.FLOWS[flow_type]
        if step >= len(flow):
            return None
            
        question_data = flow[step]
        return {
            "question": question_data["question"],
            "options": question_data.get("options"),
            "input_type": question_data["input_type"],
            "step_number": step + 1,
            "is_final": step == len(flow) - 1
        }

    @classmethod
    def determine_flow_from_response(cls, response: str) -> str:
        """Determine flow type from initial response"""
        response_lower = response.lower()
        
        flow_mapping = {
            "find a property to rent": ChatbotFlowType.PROPERTY_SEARCH,
            "ask about a specific property": ChatbotFlowType.RENT_INQUIRY,
            "schedule a property visit": ChatbotFlowType.SCHEDULE_VISIT,
            "general support": ChatbotFlowType.GENERAL_SUPPORT,
            "report an issue": ChatbotFlowType.BUG_REPORT,
            "give feedback": ChatbotFlowType.FEEDBACK
        }
        
        return flow_mapping.get(response_lower, ChatbotFlowType.GENERAL_SUPPORT)