"""WebSocket routes for live updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.state import state_manager
import json

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, question_id: str):
        """Connect a WebSocket for a question."""
        await websocket.accept()
        if question_id not in self.active_connections:
            self.active_connections[question_id] = []
        self.active_connections[question_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, question_id: str):
        """Disconnect a WebSocket."""
        if question_id in self.active_connections:
            self.active_connections[question_id].remove(websocket)
    
    async def broadcast(self, question_id: str, data: dict):
        """Broadcast data to all connections for a question."""
        if question_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[question_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[question_id].remove(conn)


connection_manager = ConnectionManager()


@router.websocket("/ws/{question_id}")
async def websocket_endpoint(websocket: WebSocket, question_id: str):
    """WebSocket endpoint for live updates."""
    await connection_manager.connect(websocket, question_id)
    
    try:
        # Send initial data
        question_state = state_manager.get_question(question_id)
        if question_state:
            await websocket.send_json({
                "type": "initial",
                "suggestions": [s.model_dump() for s in question_state.suggestions],
                "bubbles": question_state.live_bubbles
            })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "ack", "message": "Received"})
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, question_id)


async def broadcast_suggestion_update(question_id: str):
    """Broadcast suggestion updates to all connected clients."""
    question_state = state_manager.get_question(question_id)
    if question_state:
        await connection_manager.broadcast(question_id, {
            "type": "suggestions_updated",
            "suggestions": [s.model_dump() for s in question_state.suggestions]
        })


async def broadcast_bubble_update(question_id: str, bubble: dict):
    """Broadcast a new bubble to all connected clients."""
    await connection_manager.broadcast(question_id, {
        "type": "new_bubble",
        "bubble": bubble
    })

