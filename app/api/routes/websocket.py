"""
WebSocket endpoint for live updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set
import json
from app.state import get_question_state
from app.api.schemas import Suggestion

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, question_id: str):
        """Connect a client to a question's WebSocket"""
        await websocket.accept()
        if question_id not in self.active_connections:
            self.active_connections[question_id] = set()
        self.active_connections[question_id].add(websocket)
    
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


manager = ConnectionManager()


@router.websocket("/{question_id}")
async def websocket_endpoint(websocket: WebSocket, question_id: str):
    """
    WebSocket endpoint for live updates
    
    WS /ws/{question_id}
    Streams: new Suggestions updates as they're generated
    """
    # Verify question exists
    question_state = get_question_state(question_id)
    if not question_state:
        await websocket.close(code=1008, reason="Question not found")
        return
    
    # Connect client
    await manager.connect(websocket, question_id)
    
    try:
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

