"""
Service for generating summaries and classifications
"""
from typing import Optional
from app.state import get_question_state


async def generate_two_word_summary(message: str) -> str:
    """
    Generate a 2-word summary of a message
    
    Args:
        message: Message text
        
    Returns:
        2-word summary
    """
    # TODO: Implement 2-word summary generation
    # - Use AI to extract key 2-word phrase
    # - Could use keyword extraction or LLM
    
    return "summary placeholder"


async def classify_message(message: str) -> str:
    """
    Classify a message as sophisticated, simple, or neutral
    
    Args:
        message: Message text
        
    Returns:
        Classification: "sophisticated", "simple", or "neutral"
    """
    # TODO: Implement message classification
    # - Analyze message complexity
    # - Check length, vocabulary, structure
    # - Classify based on criteria
    
    return "neutral"


async def summarize_followup_messages(user_id: str, question_id: str) -> Optional[str]:
    """
    Summarize all followup messages from a user for a question
    
    Args:
        user_id: Discord user ID
        question_id: Question ID
        
    Returns:
        Summary of all messages, or None if no followup messages
    """
    # TODO: Implement followup message summarization
    # - Get all messages from user for this question
    # - If multiple messages, summarize them
    # - Return summary or None if single message
    
    question_state = get_question_state(question_id)
    if not question_state:
        return None
    
    user_messages = [
        msg for msg in question_state.discord_messages
        if msg.user_id == user_id
    ]
    
    if len(user_messages) <= 1:
        return None
    
    # TODO: Generate summary of multiple messages
    return "Summarized messages from user"

