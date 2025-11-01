"""
Dashboard data endpoint
"""
from fastapi import APIRouter, HTTPException
from app.api.schemas import SuggestionsResponse
from app.state import get_question_state

router = APIRouter()


@router.get("/dashboard/{question_id}", response_model=SuggestionsResponse)
async def get_dashboard_data(question_id: str) -> SuggestionsResponse:
    """
    Get dashboard data for a question
    
    GET /api/dashboard/{question_id}
    Response: List of Suggestion objects (matches TypeScript Suggestions type)
    """
    question_state = get_question_state(question_id)
    
    if not question_state:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Return suggestions from state
    # If no suggestions yet, return empty list
    return question_state.suggestions or []

