"""
Board.Support Chat Controller
Handles chat-related operations through Board.Support integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from authMiddleware.authMiddleware import check_for_authentication_cookie
from services.boardSupportService import board_support_service

router = APIRouter(prefix="/api/chat", tags=["Board.Support Chat"])

# Pydantic models for request/response
class CreateUserRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    user_type: Optional[str] = "user"

class CreateConversationRequest(BaseModel):
    user_id: str
    title: Optional[str] = ""
    department: Optional[str] = None

class SendMessageRequest(BaseModel):
    user_id: str
    conversation_id: str
    message: str
    attachments: Optional[List[List[str]]] = None

class ChatBotRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

# Public endpoints (no authentication required for chat functionality)
@router.post("/users", summary="Create a new chat user")
async def create_chat_user(request: CreateUserRequest):
    """Create a new user in Board.Support system"""
    try:
        result = await board_support_service.create_user(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            user_type=request.user_type
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", summary="Get chat user details")
async def get_chat_user(user_id: str):
    """Get user details from Board.Support"""
    try:
        result = await board_support_service.get_user(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations", summary="Create a new conversation")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation in Board.Support"""
    try:
        result = await board_support_service.create_conversation(
            user_id=request.user_id,
            title=request.title,
            department=request.department
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations", summary="Get conversations")
async def get_conversations(
    user_id: Optional[str] = Query(None, description="User ID to filter conversations"),
    pagination: int = Query(0, description="Pagination offset")
):
    """Get conversations from Board.Support"""
    try:
        result = await board_support_service.get_conversations(
            user_id=user_id,
            pagination=pagination
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/messages", summary="Get conversation messages")
async def get_conversation_messages(
    conversation_id: str,
    user_id: Optional[str] = Query(None, description="User ID")
):
    """Get messages from a specific conversation"""
    try:
        result = await board_support_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages", summary="Send a message")
async def send_message(request: SendMessageRequest):
    """Send a message to a conversation"""
    try:
        result = await board_support_service.send_message(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
            attachments=request.attachments
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot", summary="Get bot response")
async def get_bot_response(request: ChatBotRequest):
    """Get AI bot response from Board.Support"""
    try:
        result = await board_support_service.get_bot_response(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/search", summary="Search knowledge base")
async def search_articles(
    q: str = Query(..., description="Search query"),
    language: str = Query("en", description="Language code")
):
    """Search Board.Support knowledge base articles"""
    try:
        result = await board_support_service.search_articles(
            search_query=q,
            language=language
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/online", summary="Check if agents are online")
async def check_agents_online():
    """Check if any support agents are currently online"""
    try:
        result = await board_support_service.check_agents_online()
        return {"success": True, "agents_online": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints (authentication required)
@router.get("/admin/settings", 
           summary="Get Board.Support settings", 
           dependencies=[Depends(check_for_authentication_cookie)])
async def get_chat_settings():
    """Get Board.Support configuration settings (Admin only)"""
    try:
        result = await board_support_service.get_settings()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget", summary="Get chat widget embed code")
async def get_chat_widget():
    """Get the HTML embed code for Board.Support chat widget"""
    
    # Basic widget embed code - you'll need to customize this with your actual Board.Support installation
    widget_code = """
    <script>
        window.SBF = null;
        var script = document.createElement('script');
        script.src = 'https://cloud.board.support/script/js/supportboard.js';
        script.onload = function() {
            SBF.init({
                // Your Board.Support configuration
                // You'll need to replace these with your actual settings
                token: '', // Your Board.Support token if needed
                chat: {
                    enabled: true
                }
            });
        };
        document.head.appendChild(script);
        
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cloud.board.support/script/css/supportboard.css';
        document.head.appendChild(link);
        
        // Create chat div
        var chatDiv = document.createElement('div');
        chatDiv.id = 'supportboard';
        document.body.appendChild(chatDiv);
    </script>
    """
    
    return {
        "success": True,
        "widget_code": widget_code.strip(),
        "instructions": "Embed this code in your HTML pages to display the Board.Support chat widget"
    }