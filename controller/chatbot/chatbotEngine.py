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
                    "Report an issue",
                    "Give feedback"
                ],
                "input_type": "choice",
                "next_flow": {
                    "Find a property to rent": "property_search",
                    "Ask about a specific property": "rent_inquiry",
                    "Schedule a property visit": "schedule_visit", 
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
             "options": ["Parking", "Gym", "Swimming Pool", "Security", "None specific"], "input_type": "choice"},
            {"question": "Please provide your email address so our team can contact you with suitable property options:", 
             "input_type": "email", "is_final": False}
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
            {"question": "Which property would you like to visit?", "input_type": "text"}
            # Note: This flow uses dynamic questions handled by ChatbotScheduleVisitController
            # Subsequent questions are generated dynamically based on user responses:
            # - Property keyword search and selection (dynamic)
            # - Preferred date selection (dynamic)
            # - Time selection (dynamic)
            # - Contact details collection (dynamic)
            # - ScheduleMeeting record creation (dynamic)
        ],
        
        "bug_report": [
            {"question": "What type of issue would you like to report?", 
             "options": ["Website bug", "Property not found error", "Search not working", "Other technical issue"], 
             "input_type": "choice"}
            # Note: This flow uses dynamic questions handled by ChatbotBugReportController
            # Subsequent questions are generated dynamically based on issue type:
            # - Issue category specific questions (dynamic)
            # - Problem description and details (dynamic)
            # - Contact information collection (dynamic)
            # - Issue submission and tracking (dynamic)
        ],
        
        "feedback": [
            {"question": "What aspect would you like to give feedback about?", 
             "options": ["Property search experience", "Website usability", "Property listings quality", "Customer support", "Property visit experience", "Overall service"], 
             "input_type": "choice"}
            # Note: This flow uses dynamic questions handled by ChatbotFeedbackController  
            # Subsequent questions are generated dynamically based on feedback category:
            # - Category specific rating questions (dynamic)
            # - Detailed feedback collection (dynamic)
            # - Suggestions and improvements (dynamic)
            # - Contact information for follow-up (dynamic)
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
            "is_final": question_data.get("is_final", step == len(flow) - 1)
        }

    @classmethod
    def determine_flow_from_response(cls, response: str) -> str:
        """Determine flow type from initial response"""
        response_lower = response.lower()
        
        flow_mapping = {
            "find a property to rent": ChatbotFlowType.PROPERTY_SEARCH,
            "ask about a specific property": ChatbotFlowType.RENT_INQUIRY,
            "schedule a property visit": ChatbotFlowType.SCHEDULE_VISIT,
            "report an issue": ChatbotFlowType.BUG_REPORT,
            "give feedback": ChatbotFlowType.FEEDBACK
        }
        
        return flow_mapping.get(response_lower, ChatbotFlowType.BUG_REPORT)