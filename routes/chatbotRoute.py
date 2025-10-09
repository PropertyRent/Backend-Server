from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from controller.chatbot.mainChatbotController import MainChatbotController
from schemas.chatbotSchemas import StartChatRequest, ChatResponse, SatisfactionResponse
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["Chatbot"])


# === PUBLIC CHATBOT ROUTES ===
# No authentication required - accessible to all users

@router.post("/chatbot/start",
    summary="Start a new chatbot conversation"
)
async def start_chat(request: Request, chat_request: StartChatRequest):
    """
    Start a new chatbot conversation or resume an existing one.
    
    **How it works:**
    - Creates new conversation session if no session_id provided
    - Resumes existing conversation if session_id provided
    - Returns the first question to get started
    
    **Example Response:**
    ```json
    {
        "session_id": "uuid-here",
        "question": "Hi! I'm your property assistant. How can I help you today?",
        "options": ["Find a property to rent", "Ask about a specific property", ...],
        "input_type": "choice"
    }
    ```
    """
    # Get client IP for tracking
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return await MainChatbotController.handle_start_chat(
        session_id=chat_request.session_id,
        user_agent=user_agent,
        user_ip=client_ip
    )


@router.post("/chatbot/respond",
    summary="Send user response and get next question"
)
async def chat_respond(response: ChatResponse):
    """
    Send user's response to current question and get the next question.
    
    **Flow:**
    1. User selects/types response to current question
    2. System processes response and determines next question
    3. Returns next question or satisfaction survey if flow complete
    
    **Example Request:**
    ```json
    {
        "session_id": "uuid-here",
        "user_response": "Find a property to rent"
    }
    ```
    """
    return await MainChatbotController.handle_chat_response(
        session_id=response.session_id,
        user_response=response.user_response
    )


@router.post("/chatbot/satisfaction",
    summary="Submit final satisfaction response"
)
async def submit_satisfaction(satisfaction: SatisfactionResponse):
    """
    Submit satisfaction response and complete conversation.
    
    **Outcomes:**
    - If satisfied: Conversation marked as completed
    - If not satisfied: Creates escalation for admin review
    
    **Example Request:**
    ```json
    {
        "session_id": "uuid-here", 
        "is_satisfied": false,
        "feedback": "Need more help with pricing"
    }
    ```
    """
    return await MainChatbotController.handle_satisfaction_response(
        session_id=satisfaction.session_id,
        is_satisfied=satisfaction.is_satisfied,
        feedback=satisfaction.feedback
    )




@router.get("/admin/chatbot/conversations",
    summary="[ADMIN] Get all chatbot conversations",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Conversations per page"),
    status: Optional[str] = Query(None, description="Filter by status (active, completed, escalated, abandoned)")
):
    """
    Get all chatbot conversations for admin dashboard.
    
    **Features:**
    - Pagination support
    - Filter by conversation status
    - Shows conversation summary with message count
    - Indicates which conversations have escalations
    
    **Status Options:**
    - `active`: Ongoing conversations
    - `completed`: Successfully finished conversations  
    - `escalated`: Conversations needing admin attention
    - `abandoned`: Conversations left incomplete
    """
    return await MainChatbotController.handle_get_conversations(
        page=page,
        limit=limit,
        status=status
    )


@router.get("/admin/chatbot/conversations/{conversation_id}",
    summary="[ADMIN] Get detailed conversation with all messages",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_conversation_details(conversation_id: str):
    """
    Get complete conversation details including all messages and escalations.
    
    **Includes:**
    - Full conversation metadata
    - All questions and user responses in order
    - Response times for each interaction
    - Any escalation details if conversation needs admin attention
    - User satisfaction rating
    
    **Use Cases:**
    - Review customer interactions
    - Analyze conversation quality
    - Handle escalated support requests
    - Improve chatbot flows based on user responses
    """
    return await MainChatbotController.handle_get_conversation_details(conversation_id)


@router.get("/admin/chatbot/stats",
    summary="[ADMIN] Get chatbot analytics and statistics",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_chatbot_stats():
    """
    Get comprehensive chatbot analytics and performance metrics.
    
    **Metrics Include:**
    - Total conversations by status
    - Average conversation completion time
    - Most common conversation flows
    - Satisfaction ratings distribution
    - Escalation reasons analysis
    - Peak usage times
    """
    # This will be implemented based on specific analytics needs
    from datetime import datetime, timedelta
    from model.chatbotModel import ChatbotConversation, ChatbotEscalation
    
    try:
        # Basic stats
        total_conversations = await ChatbotConversation.all().count()
        completed_conversations = await ChatbotConversation.filter(status="completed").count()
        escalated_conversations = await ChatbotConversation.filter(status="escalated").count()
        active_conversations = await ChatbotConversation.filter(status="active").count()
        
        # Satisfaction stats
        satisfied_count = await ChatbotConversation.filter(is_satisfied=True).count()
        unsatisfied_count = await ChatbotConversation.filter(is_satisfied=False).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_conversations = await ChatbotConversation.filter(created_at__gte=week_ago).count()
        
        return {
            "success": True,
            "data": {
                "total_conversations": total_conversations,
                "status_breakdown": {
                    "completed": completed_conversations,
                    "escalated": escalated_conversations,
                    "active": active_conversations,
                    "abandoned": total_conversations - completed_conversations - escalated_conversations - active_conversations
                },
                "satisfaction": {
                    "satisfied": satisfied_count,
                    "unsatisfied": unsatisfied_count,
                    "satisfaction_rate": round((satisfied_count / (satisfied_count + unsatisfied_count)) * 100, 2) if (satisfied_count + unsatisfied_count) > 0 else 0
                },
                "recent_activity": {
                    "conversations_last_7_days": recent_conversations
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting chatbot stats: {e}")
        return {
            "success": False,
            "message": f"Failed to get stats: {str(e)}"
        }