"""
Question creation endpoint
"""

from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.api.schemas import QuestionRequest, QuestionResponse
from app.config import settings
from app.state import create_question_state
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

    # Create question state
    question_state = create_question_state(question_id, request.question)

    # Scrape Discord history for relevant messages
    messages = await scrape_discord_history(request.question)

    # Add messages to state
    for message in messages:
        question_state.discord_messages.append(message)

    # Send DMs to introverted users
    await send_dm_to_introverted_users(question_id, request.question)

    # Construct dashboard URL
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"

    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url,
    )
