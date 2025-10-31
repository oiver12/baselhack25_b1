"""API routes for question management."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.schemas import QuestionRequest, QuestionResponse
from app.config import settings
from app.state import state_manager
from app.services.discord_service import DiscordService

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("", response_model=QuestionResponse, status_code=201)
async def create_question(
    request: QuestionRequest,
    background_tasks: BackgroundTasks
) -> QuestionResponse:
    """Create a new question/discussion session."""
    # Create question in state
    question_id = state_manager.create_question(request.question)
    
    # Start background task to scrape Discord history
    background_tasks.add_task(
        scrape_discord_history,
        question_id=question_id,
        question=request.question
    )
    
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"
    
    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url
    )


async def scrape_discord_history(question_id: str, question: str) -> None:
    """Background task to scrape Discord chat history for the question."""
    try:
        discord_service = DiscordService()
        messages = await discord_service.scrape_relevant_messages(question)
        
        # Add messages to state
        question_state = state_manager.get_question(question_id)
        if question_state:
            for msg in messages:
                question_state.add_message(msg)
            
            # Trigger analysis to generate suggestions
            from app.services.suggestions_service import SuggestionsService
            suggestions_service = SuggestionsService()
            suggestions = await suggestions_service.generate_suggestions(question_state)
            state_manager.update_suggestions(question_id, suggestions)
    except Exception as e:
        print(f"Error scraping Discord history: {e}")

