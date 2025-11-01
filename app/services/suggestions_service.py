"""
Service for generating Suggestions from Discord messages
"""
from typing import List
from app.state import DiscordMessage, get_question_state
from app.api.schemas import Suggestion, PersonOpinion
from app.services.analysis_service import (
    extract_themes,
    extract_pros_and_cons,
    cluster_messages,
)
from app.services.summary_service import (
    generate_two_word_summary,
    classify_message,
    find_excellent_message,
    summarize_followup_messages,
)


async def generate_suggestions(question_id: str) -> List[Suggestion]:
    """
    Generate Suggestions array from Discord messages
    
    Args:
        question_id: The question ID
        
    Returns:
        List of Suggestion objects matching TypeScript type
    """
    question_state = get_question_state(question_id)
    if not question_state:
        return []
    
    messages = question_state.discord_messages
    
    # Classify ALL messages once upfront (using cache if available)
    all_message_texts = [msg.content for msg in messages]
    all_classifications = await classify_message(all_message_texts, question_id=question_id)
    
    # Create a mapping from message content to classification for reuse
    message_to_classification = dict(zip(all_message_texts, all_classifications))
    
    # Find excellent message once (using cache if available)
    excellent_message = await find_excellent_message(all_message_texts, all_classifications, question_id=question_id)
    
    # Cluster messages by theme - always cluster all messages
    clusters = await cluster_messages(messages)
    
    suggestions: List[Suggestion] = []
    
    for theme_title, theme_messages in clusters.items():
        # Aggregate pros and cons for this theme
        all_pros = []
        all_contra = []
        
        # Collect people opinions
        people_opinions: List[PersonOpinion] = []
        
        for message in theme_messages:
            # Extract pros/cons from message
            pros_cons = await extract_pros_and_cons(message.content)
            all_pros.extend(pros_cons["pros"])
            all_contra.extend(pros_cons["contra"])
            
            # Create person opinion
            # Check if there are followup messages from this user
            followup_summary = await summarize_followup_messages(message.user_id, question_id)
            message_text = followup_summary if followup_summary else message.content
            
            # Reuse pre-computed classification instead of calling again
            classification = message_to_classification.get(message.content, "neutral")
            
            people_opinions.append(
                PersonOpinion(
                    name=message.username,
                    profile_pic_url=message.profile_pic_url,
                    message=message_text,
                    classification=classification,
                )
            )
        
        # Calculate size (0-1) based on support/engagement
        size = await calculate_suggestion_size(theme_messages, messages)
        
        # Create suggestion
        suggestion = Suggestion(
            title=theme_title,
            size=size,
            pros=list(set(all_pros)),  # Remove duplicates
            contra=list(set(all_contra)),  # Remove duplicates
            people_opinions=people_opinions,
        )
        
        suggestions.append(suggestion)
    
    return suggestions


async def calculate_suggestion_size(
    theme_messages: List[DiscordMessage],
    all_messages: List[DiscordMessage],
) -> float:
    """
    Calculate the size (0-1) of a suggestion based on support/engagement
    
    Args:
        theme_messages: Messages for this suggestion
        all_messages: All messages in the discussion
        
    Returns:
        Size value between 0 and 1
    """
    # TODO: Implement size calculation
    # - Calculate based on message count, engagement, sentiment
    # - Normalize to 0-1 range
    
    if not all_messages:
        return 0.0
    
    return len(theme_messages) / len(all_messages)


async def update_suggestions_for_question(question_id: str) -> List[Suggestion]:
    """
    Update and store suggestions for a question
    
    Args:
        question_id: The question ID
        
    Returns:
        Updated list of Suggestions
    """
    suggestions = await generate_suggestions(question_id)
    
    # Update state
    question_state = get_question_state(question_id)
    if question_state:
        question_state.suggestions = suggestions
    
    # Broadcast via WebSocket
    from app.api.routes.websocket import broadcast_suggestions_update
    await broadcast_suggestions_update(question_id, suggestions)
    
    return suggestions

