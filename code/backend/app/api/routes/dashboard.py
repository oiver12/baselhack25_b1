"""
Dashboard data endpoint
"""
from fastapi import APIRouter, HTTPException
from app.state import get_active_question

router = APIRouter()


@router.get("/dashboard/{question_id}")
async def get_dashboard_data(question_id: str):
    """
    Get dashboard data for the active question
    
    GET /api/dashboard/{question_id}
    Response: Question state with messages and participants
    Verifies question_id matches active question for backward compatibility
    """
    question_state = get_active_question()
    
    if not question_state:
        raise HTTPException(status_code=404, detail="No active question")
    
    # Verify question_id matches active question (backward compatibility)
    if question_state.question_id != question_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Return empty list if there are fewer than 5 relevant messages
    if len(question_state.discord_messages) < 5:
        return []
    
    # Return question state
    # Format: Suggestions[]
    # Example object for reference:
    # {
    #   "title": "Summary Title",
    #   "size": 0.34,
    #   "peopleOpinions": [
    #     {
    #       "name": "Person",
    #       "profilePicUrl": "...",
    #       "message": "...",
    #       "classification": "good",
    #       "isExcellent": false
    #     }
    #   ]
    # }
    suggestions = []

    # Use the 2-word summaries as the cluster titles (Suggestions.title)
    for i, two_word_title in enumerate(getattr(question_state, "two_word_summaries", []) or []):
        # Collect all messages associated with this 2-word summary (cluster)
        cluster_messages = [
            msg for msg in question_state.discord_messages
            if (getattr(msg, "two_word_summary", None) or "") == two_word_title
        ]
        # If no messages, skip this suggestion
        if not cluster_messages:
            continue

        # Heuristic for cluster "size" (normalized to 0-1)
        size = len(cluster_messages) / max(1, len(question_state.discord_messages))

        # People opinions for this cluster
        people_opinions = []
        for msg in cluster_messages:
            people_opinions.append({
                "name": msg.username,
                "profilePicUrl": msg.profile_pic_url,
                "message": msg.content,
                "classification": (msg.classification if msg.classification in ["positive", "neutral", "negative"] else "neutral"),
                "isExcellent": bool(getattr(msg, "is_excellent", False)),
            })

        suggestions.append({
            "title": two_word_title,
            "size": size,
            "peopleOpinions": people_opinions
        })

    return suggestions

