"""
Messages endpoint for getting all Discord messages
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.state import global_historical_messages, questions, DiscordMessage

router = APIRouter()


class MessageResponse(BaseModel):
    """Discord message response model"""
    messageId: str
    userId: str
    user: str
    message: str
    profilePicUrl: str
    timestamp: str
    channelId: str
    questionId: str  # Include question ID to know which question the message belongs to
    two_word_summary: str
    classification: str
    is_excellent: bool


@router.get("/messages", response_model=List[MessageResponse])
async def get_all_messages() -> List[MessageResponse]:
    """
    Get all historical Discord messages from all channels
    
    GET /api/messages
    Response: List of all Discord messages (historical + from questions)
    """
    # Start with all historical messages from global storage
    all_discord_messages = global_historical_messages.copy()
    
    # Also include messages from all questions (may include newer messages)
    # Build a set to avoid duplicates
    message_ids_seen = {msg.message_id for msg in all_discord_messages}
    
    for question_state in questions.values():
        for msg in question_state.discord_messages:
            # Only add if not already in historical messages (avoid duplicates)
            if msg.message_id not in message_ids_seen:
                all_discord_messages.append(msg)
                message_ids_seen.add(msg.message_id)
    
    # Build a map of message_id -> question_id for messages in questions
    message_to_question = {}
    for q_id, question_state in questions.items():
        for msg in question_state.discord_messages:
            message_to_question[msg.message_id] = q_id
    
    # Convert DiscordMessage objects to MessageResponse objects
    all_messages = []
    for discord_msg in all_discord_messages:
        # Try to find which question this message belongs to
        question_id = message_to_question.get(discord_msg.message_id, None)
        
        # If not in a specific question, use empty string or None
        # You could also create a "general" question_id if needed
        all_messages.append(MessageResponse(
            messageId=discord_msg.message_id,
            userId=discord_msg.user_id,
            user=discord_msg.username,
            message=discord_msg.content,
            profilePicUrl=discord_msg.profile_pic_url,
            timestamp=discord_msg.timestamp.isoformat(),
            channelId=discord_msg.channel_id,
            questionId=question_id or "",  # Empty string if not associated with a question
            two_word_summary=discord_msg.two_word_summary or "",
            classification=discord_msg.classification or "",
            is_excellent=discord_msg.is_excellent,
        ))
    
    # Sort by timestamp (oldest first)
    all_messages.sort(key=lambda x: x.timestamp)
    
    return all_messages

