"""
Report endpoint for getting whole report with 2D visualization and summary
"""
from fastapi import APIRouter, HTTPException
from app.state import get_active_question
from app.services.report import get_whole_Report

router = APIRouter()


@router.get("/report/{question_id}")
async def get_report(question_id: str):
    """
    Get the whole report for a question including 2D coordinates and summary
    
    GET /api/report/{question_id}
    Response: {
        "results": [
            {
                "message_id": str,
                "x": float,
                "y": float,
                "message": str,
                "name": str,
                "profile_pic_url": str
            }
        ],
        "summary": {
            "summary": str,
            "points": [...]
        }
    }
    """
    question_state = get_active_question()
    
    if not question_state:
        raise HTTPException(status_code=404, detail="No active question")
    
    # Verify question_id matches active question
    if question_state.question_id != question_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get the whole report
    report = await get_whole_Report(question_state)
    
    return report

