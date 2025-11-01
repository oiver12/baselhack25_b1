"""
WebSocket endpoint for live updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set, Optional
import json
import asyncio
from app.state import get_question_state
from app.api.schemas import Suggestion
from app.config import settings

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.all_messages_connections: Set[WebSocket] = set()  # For global all-messages endpoint

    def _is_allowed_origin(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed"""
        # If "*" is in CORS_ORIGINS, allow all origins
        if "*" in settings.CORS_ORIGINS:
            return True

        # If no origin header is provided, allow (some WebSocket clients don't send it)
        if not origin:
            return True

        # Check if origin is in allowed list
        return origin in settings.CORS_ORIGINS

    async def connect(self, websocket: WebSocket, question_id: str):
        """Connect a client to a question's WebSocket with origin validation"""
        # Get origin from headers (case-insensitive)
        origin = websocket.headers.get("origin") or websocket.headers.get("Origin")

        # Accept the connection first (required by FastAPI)
        await websocket.accept()

        # Validate origin after accepting (can close if invalid)
        if not self._is_allowed_origin(origin):
            await websocket.close(code=1008, reason="Origin not allowed")
            return False

        if question_id not in self.active_connections:
            self.active_connections[question_id] = set()
        self.active_connections[question_id].add(websocket)
        return True

    def disconnect(self, websocket: WebSocket, question_id: str):
        """Disconnect a client from a question's WebSocket"""
        if question_id in self.active_connections:
            self.active_connections[question_id].discard(websocket)

    async def broadcast_to_question(self, question_id: str, data: dict):
        """Broadcast data to all clients connected to a question"""
        if question_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[question_id]:
                try:
                    await connection.send_json(data)
                except:
                    disconnected.add(connection)
            # Remove disconnected clients
            for conn in disconnected:
                self.active_connections[question_id].discard(conn)
    
    async def broadcast_to_all_messages(self, data: dict):
        """Broadcast data to all clients connected to the all-messages endpoint"""
        disconnected = set()
        for connection in self.all_messages_connections:
            try:
                await connection.send_json(data)
            except:
                disconnected.add(connection)
        # Remove disconnected clients
        for conn in disconnected:
            self.all_messages_connections.discard(conn)


manager = ConnectionManager()


@router.websocket("/{question_id}")
async def websocket_endpoint(websocket: WebSocket, question_id: str):
    """
    WebSocket endpoint for live updates

    WS /ws/{question_id}
    Streams: new Suggestions updates as they're generated

    Accepts connections from allowed origins (configured via CORS_ORIGINS).
    No authentication required - connections are open for development.
    """
    # Connect client (this validates origin and accepts connection)
    connected = await manager.connect(websocket, question_id)
    if not connected:
        return  # Connection was rejected due to origin validation

    # Verify question exists after connection is accepted
    question_state = get_question_state(question_id)
    if not question_state:
        await websocket.close(code=1008, reason="Question not found")
        manager.disconnect(websocket, question_id)
        return

    try:
        # Send connected message
        connected_data = {
            "type": "connected",
            "message": "WebSocket connected successfully",
        }
        await websocket.send_json(connected_data)

        # Send existing Discord messages with a small delay so they "fly through"
        for discord_msg in question_state.discord_messages:
            message_data = {
                "type": "message",
                "user": discord_msg.username,
                "message": discord_msg.content,
                "profilePicUrl": discord_msg.profile_pic_url,
            }
            await websocket.send_json(message_data)
            await asyncio.sleep(0.1)  # 100ms delay between historical messages

        # Send initial state
        initial_data = {
            "type": "initial",
            "suggestions": [s.model_dump() for s in question_state.suggestions],
        }
        await websocket.send_json(initial_data)

        # Keep connection alive and wait for messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            # For now, just keep connection alive
            pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, question_id)
    except Exception as e:
        manager.disconnect(websocket, question_id)
        raise


async def broadcast_suggestions_update(question_id: str, suggestions: list[Suggestion]):
    """Broadcast updated suggestions to all connected clients"""
    data = {
        "type": "suggestions_update",
        "suggestions": [s.model_dump() for s in suggestions],
    }
    await manager.broadcast_to_question(question_id, data)


async def broadcast_discord_message(
    question_id: str, 
    username: str, 
    message: str, 
    profile_pic_url: str,
    message_id: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    channel_id: Optional[str] = None
):
    """Broadcast a Discord message to all connected clients"""
    # Basic message format (for backward compatibility)
    basic_data = {
        "type": "message",
        "user": username,
        "message": message,
        "profilePicUrl": profile_pic_url,
    }
    await manager.broadcast_to_question(question_id, basic_data)
    
    # Enhanced message format (for messages endpoint with full details)
    if message_id and user_id:
        enhanced_data = {
            "type": "message",
            "messageId": message_id,
            "userId": user_id,
            "user": username,
            "message": message,
            "profilePicUrl": profile_pic_url,
            "timestamp": timestamp or "",
            "channelId": channel_id or "",
        }
        await manager.broadcast_to_question(question_id, enhanced_data)


@router.websocket("/messages/{question_id}")
async def messages_websocket_endpoint(websocket: WebSocket, question_id: str):
    """
    WebSocket endpoint specifically for receiving only NEW Discord messages
    
    WS /ws/messages/{question_id}
    
    Streams only NEW Discord messages in real-time (no historical messages).
    Only messages that arrive after connection will be sent.
    
    Message format:
    {
        "type": "message",
        "messageId": "string",
        "userId": "string",
        "user": "string",
        "message": "string",
        "profilePicUrl": "string",
        "timestamp": "ISO8601 string",
        "channelId": "string"
    }
    """
    # Connect client (validates origin and accepts connection)
    connected = await manager.connect(websocket, question_id)
    if not connected:
        return  # Connection was rejected due to origin validation
    
    # Verify question exists
    question_state = get_question_state(question_id)
    if not question_state:
        await websocket.close(code=1008, reason="Question not found")
        manager.disconnect(websocket, question_id)
        return
    
    try:
        # Send connected message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Discord messages stream - waiting for new messages",
            "questionId": question_id
        })
        
        # Don't send historical messages - only wait for new ones
        # New messages will be broadcast automatically via broadcast_discord_message()
        # which uses the same connection manager
        while True:
            # Listen for any client messages (ping/pong, etc.)
            try:
                data = await websocket.receive_text()
                # Echo back or handle client messages if needed
                await websocket.send_json({
                    "type": "pong",
                    "message": "Connection alive"
                })
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, question_id)
    except Exception as e:
        manager.disconnect(websocket, question_id)
        raise
