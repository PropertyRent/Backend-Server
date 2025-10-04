"""
Board.Support Chat Service Integration
Provides chatbot functionality through Board.Support API
"""

import httpx
import json
import os
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
import asyncio

class BoardSupportService:
    def __init__(self):
        # Configuration from environment variables
        self.api_url = os.getenv("BOARD_SUPPORT_API_URL", "https://cloud.board.support/script/include/api.php")
        self.admin_token = os.getenv("BOARD_SUPPORT_ADMIN_TOKEN", "")  # Your admin token
        self.timeout = 30
        
    async def _make_api_call(self, function: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API call to Board.Support"""
        if not self.admin_token:
            raise HTTPException(status_code=500, detail="Board.Support admin token not configured")
            
        data = {
            "token": self.admin_token,
            "function": function
        }
        
        if params:
            data.update(params)
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.api_url, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Board.Support API error: {str(e)}")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid response from Board.Support API")

    async def create_user(self, first_name: str, last_name: str = "", email: str = "", 
                         user_type: str = "user") -> Dict[str, Any]:
        """Create a new user in Board.Support"""
        params = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "user_type": user_type
        }
        return await self._make_api_call("add-user", params)

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user details"""
        params = {"user_id": user_id}
        return await self._make_api_call("get-user", params)

    async def create_conversation(self, user_id: str, title: str = "", 
                                 department: str = None) -> Dict[str, Any]:
        """Create a new conversation"""
        params = {
            "user_id": user_id,
            "title": title
        }
        if department:
            params["department"] = department
            
        return await self._make_api_call("new-conversation", params)

    async def send_message(self, user_id: str, conversation_id: str, 
                          message: str, attachments: List[List[str]] = None) -> Dict[str, Any]:
        """Send a message to a conversation"""
        params = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message": message
        }
        if attachments:
            params["attachments"] = json.dumps(attachments)
            
        return await self._make_api_call("send-message", params)

    async def get_conversations(self, user_id: str = None, pagination: int = 0) -> Dict[str, Any]:
        """Get conversations"""
        params = {"pagination": pagination}
        if user_id:
            params["user_id"] = user_id
            return await self._make_api_call("get-user-conversations", params)
        else:
            return await self._make_api_call("get-conversations", params)

    async def get_conversation_messages(self, conversation_id: str, 
                                      user_id: str = None) -> Dict[str, Any]:
        """Get conversation messages"""
        params = {"conversation_id": conversation_id}
        if user_id:
            params["user_id"] = user_id
            
        return await self._make_api_call("get-conversation", params)

    async def search_articles(self, search_query: str, language: str = "en") -> Dict[str, Any]:
        """Search knowledge base articles"""
        params = {
            "search": search_query,
            "articles_language": language
        }
        return await self._make_api_call("search-articles", params)

    async def get_bot_response(self, message: str, conversation_id: str = None, 
                              user_id: str = None) -> Dict[str, Any]:
        """Get bot response (if AI is configured)"""
        params = {
            "message": message
        }
        if conversation_id:
            params["conversation_id"] = conversation_id
        if user_id:
            params["recipient_id"] = user_id
            
        # This would use Dialogflow or OpenAI integration if configured
        return await self._make_api_call("dialogflow-message", params)

    async def check_agents_online(self) -> bool:
        """Check if any agents are online"""
        result = await self._make_api_call("agents-online")
        return result.get("response", False)

    async def get_settings(self) -> Dict[str, Any]:
        """Get Board.Support settings"""
        return await self._make_api_call("get-settings")

# Service instance
board_support_service = BoardSupportService()