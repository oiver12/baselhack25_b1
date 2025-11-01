"""
Discord service for scraping messages and sending DMs
"""
from datetime import datetime
from typing import List
from app.state import DiscordMessage, get_question_state


async def scrape_discord_history(question: str) -> List[DiscordMessage]:
    """
    Scrape Discord chat history for messages relevant to the question
    
    Args:
        question: The question to search for relevant messages
        
    Returns:
        List of relevant Discord messages
    """
    # TODO: Implement Discord API scraping logic
    # - Search through Discord channel history
    # - Filter messages relevant to the question
    # - Extract user info, content, timestamps
    # - Return as DiscordMessage objects
    
    messages: List[DiscordMessage] = []
    return messages


async def send_dm_to_introverted_users(question_id: str, question: str) -> None:
    """
    Send DMs to introverted users asking for their views
    
    Args:
        question_id: The question ID
        question: The question text
    """
    # TODO: Implement DM sending logic
    # - Identify introverted users (based on message frequency, etc.)
    # - Send DM with question and link to dashboard
    # - Track which users received DMs in question state
    
    question_state = get_question_state(question_id)
    if question_state:
        # Mark participants as DM sent
        pass


async def listen_for_new_messages(question_id: str) -> None:
    """
    Listen for new Discord messages related to a question
    
    Args:
        question_id: The question ID to listen for
    """
    # TODO: Implement Discord event listener
    # - Listen to Discord channel for new messages
    # - Filter for relevance to question
    # - Process and add to question state
    # - Trigger suggestions update
    
    pass


async def get_user_profile(user_id: str) -> dict:
    """
    Get Discord user profile information
    
    Args:
        user_id: Discord user ID
        
    Returns:
        Dictionary with username, profile_pic_url, etc.
    """
    # TODO: Implement user profile fetching
    # - Fetch user info from Discord API
    # - Return username, avatar URL, etc.
    
    return {
        "username": "",
        "profile_pic_url": "",
    }

