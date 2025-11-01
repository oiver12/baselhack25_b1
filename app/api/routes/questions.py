"""
Question creation endpoint
"""

from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from app.api.schemas import QuestionRequest, QuestionResponse, QuestionInfo
from app.config import settings
from app.state import create_question_state, questions, global_historical_messages
from app.services.discord_service import (
    scrape_discord_history,
    send_dm_to_introverted_users,
)

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse)
async def create_question(request: QuestionRequest) -> QuestionResponse:
    """
    Create a new discussion question

    POST /api/questions
    Body: {"question": "How should we change..."}
    Response: {"question_id": "uuid", "dashboard_url": "..."}
    """
    # Generate unique question ID
    question_id = str(uuid4())
    print(question_id)
    print(request.question)
    
    # Create the question state immediately
    create_question_state(question_id, request.question)
    
    # Post the new question to Discord
    from app.discord_bot.bot import get_bot_instance
    import asyncio
    bot = get_bot_instance()
    if bot and bot.is_ready():
        # Just send to the first public text channel as a simple implementation
        # Need to run in bot's event loop, not FastAPI's loop
        bot_loop = bot.loop
        current_loop = asyncio.get_event_loop()
        
        async def _post_question():
            posted = False
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages and not posted:
                        message_content = f"!start_discussion: {request.question}"
                        await channel.send(message_content)
                        posted = True
                        break
                if posted:
                    break
            return posted
        
        if bot_loop != current_loop:
            # Run in bot's event loop using run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(_post_question(), bot_loop)
            try:
                future.result(timeout=10)  # 10 second timeout
            except Exception as e:
                print(f"Warning: Failed to post question to Discord: {e}")
        else:
            # Already in bot's loop, run directly
            await _post_question()
    else:
        print("Warning: Bot not available or not ready to post question to Discord.")

    # Construct dashboard URL
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"

    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url,
    )

@router.get("/question_and_ids", response_model=List[QuestionInfo])
async def get_question_ids() -> List[QuestionInfo]:
    """
    Get all question IDs and questions
    
    GET /api/question_and_ids
    Response: List of QuestionInfo objects with question_id and question
    """
    return [
        QuestionInfo(question_id=qid, question=qstate.question)
        for qid, qstate in questions.items()
    ]