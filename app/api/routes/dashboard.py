"""
Dashboard data endpoint
"""
from fastapi import APIRouter, HTTPException
from app.state import get_question_state

router = APIRouter()


@router.get("/dashboard/{question_id}")
async def get_dashboard_data(question_id: str):
    """
    Get dashboard data for a question
    
    GET /api/dashboard/{question_id}
    Response: Question state with messages and participants
    """
    question_state = get_question_state(question_id)
    
    if not question_state:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Return question state
    return {
        "question_id": question_state.question_id,
        "question": question_state.question,
        "created_at": question_state.created_at.isoformat() if hasattr(question_state.created_at, 'isoformat') else str(question_state.created_at),
        "messages": [
            {
                "message_id": msg.message_id,
                "user_id": msg.user_id,
                "username": msg.username,
                "profile_pic_url": msg.profile_pic_url,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp),
                "channel_id": msg.channel_id,
                "question_id": msg.question_id,
            }
            for msg in question_state.discord_messages
        ],
        "participants": [
            {
                "user_id": p.user_id,
                "username": p.username,
                "profile_pic_url": p.profile_pic_url,
                "message_count": p.message_count,
                "dm_sent": p.dm_sent,
            }
            for p in question_state.participants.values()
        ],
    }

