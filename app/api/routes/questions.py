"""
Question creation endpoint
"""

from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from app.api.schemas import QuestionRequest, QuestionResponse, QuestionInfo
from app.config import settings
from app.state import create_question_state, get_active_question
from app.services.discord_service import (
    scrape_discord_history,
    send_dm_to_introverted_users,
)
from app.services.question_service import analyze_historical_messages_for_question
from app.services.pipeline import process_all

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
    
    # Create the question state and set as active question (replaces any existing)
    active_question = create_question_state(question_id, request.question)
    # Save to cache
    from app.state import save_all_questions
    save_all_questions()
    
    # Analyze historical messages for relevance in background
    # This will filter messages and add relevant ones to the question
    import asyncio
    asyncio.create_task(_analyze_historical_messages(active_question))
    
    # Construct dashboard URL
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"

    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url,
    )

async def _analyze_historical_messages(question):
    """Background task to analyze historical messages for the new question"""
    try:
        print(f"Starting historical message analysis for question: {question.question}")
        # Filter historical messages and add relevant ones
        await analyze_historical_messages_for_question(question)
        
        await process_all()
        print(f"Completed historical message analysis for question: {question.question}")
    except Exception as e:
        print(f"Error analyzing historical messages: {e}")
        import traceback
        traceback.print_exc()


@router.get("/question_and_ids", response_model=List[QuestionInfo])
async def get_question_ids() -> List[QuestionInfo]:
    """
    Get active question ID and question
    
    GET /api/question_and_ids
    Response: List with single QuestionInfo object (or empty if no active question)
    """
    active_question = get_active_question()
    if active_question:
        return [QuestionInfo(question_id=active_question.question_id, question=active_question.question)]
    return []