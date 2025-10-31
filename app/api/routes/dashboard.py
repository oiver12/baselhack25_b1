"""API routes for dashboard data."""
from fastapi import APIRouter, HTTPException
from app.api.schemas import SuggestionsResponse
from app.state import state_manager

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{question_id}", response_model=SuggestionsResponse)
async def get_dashboard_data(question_id: str) -> SuggestionsResponse:
    """Get dashboard data (suggestions) for a question."""
    question_state = state_manager.get_question(question_id)
    
    if not question_state:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question_state.suggestions


@router.get("/{question_id}/bubbles")
async def get_live_bubbles(question_id: str):
    """Get live bubbles (2-word summaries) for a question."""
    question_state = state_manager.get_question(question_id)
    
    if not question_state:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {
        "bubbles": question_state.live_bubbles,
        "question_id": question_id
    }

