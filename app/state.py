"""
In-memory state management for questions and messages
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class DiscordMessage:
    """Represents a Discord message"""

    def __init__(
        self,
        message_id: str,
        user_id: str,
        username: str,
        profile_pic_url: str,
        content: str,
        timestamp: datetime,
        channel_id: str,
        question_id: Optional[str] = None,
        two_word_summary: Optional[str] = None,
        classification: Optional[str] = None,
        is_excellent: bool = False,
    ):
        self.message_id = message_id
        self.user_id = user_id
        self.username = username
        self.profile_pic_url = profile_pic_url
        self.content = content
        self.timestamp = timestamp
        self.channel_id = channel_id
        self.question_id = question_id
        self.two_word_summary = two_word_summary
        self.classification = classification
        self.is_excellent = is_excellent


class Participant:
    """Represents a participant in a discussion"""

    def __init__(
        self,
        user_id: str,
        username: str,
        profile_pic_url: str,
        message_count: int = 0,
        dm_sent: bool = False,
    ):
        self.user_id = user_id
        self.username = username
        self.profile_pic_url = profile_pic_url
        self.message_count = message_count
        self.dm_sent = dm_sent


class QuestionState:
    """State for a single question/discussion"""

    def __init__(
        self,
        question_id: str,
        question: str,
        created_at: datetime,
    ):
        self.question_id = question_id
        self.question = question
        self.created_at = created_at
        self.discord_messages: List[DiscordMessage] = []
        self.participants: Dict[str, Participant] = {}
        # Cache for message classifications (message_content -> "good"/"neutral"/"bad")
        self.message_classifications: Dict[str, str] = {}
        # Cache for excellent message
        self.excellent_message: Optional[str] = None
        # List of unique 2-word summaries for this question
        self.two_word_summaries: List[str] = []


# Global in-memory storage
questions: Dict[str, QuestionState] = {}

# Global storage for all historical Discord messages (fetched once on startup)
global_historical_messages: List[DiscordMessage] = []

# Set cache for efficient duplicate checking of message IDs
global_historical_message_ids: set = set()

# Cache directory for persistent storage
CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)


def _get_cache_file(question_id: str) -> Path:
    """Get cache file path for a question"""
    return CACHE_DIR / f"question_{question_id}.json"


def _load_cache(question_id: str, state: QuestionState) -> None:
    """Load cached classifications, excellent message, and summaries from file"""
    cache_file = _get_cache_file(question_id)
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                state.message_classifications = cache_data.get("classifications", {})
                state.excellent_message = cache_data.get("excellent_message")
                state.two_word_summaries = cache_data.get("two_word_summaries", [])
                
                # Load message summaries and classifications into message objects
                message_summaries = cache_data.get("message_summaries", {})  # message_id -> summary
                message_classifications_cache = cache_data.get("message_classifications_by_id", {})  # message_id -> classification
                excellent_message_id = cache_data.get("excellent_message_id", None)
                
                for msg in state.discord_messages:
                    if msg.message_id in message_summaries:
                        msg.two_word_summary = message_summaries[msg.message_id]
                    if msg.message_id in message_classifications_cache:
                        msg.classification = message_classifications_cache[msg.message_id]
                    if excellent_message_id and msg.message_id == excellent_message_id:
                        msg.is_excellent = True
        except (json.JSONDecodeError, KeyError):
            pass  # If cache is corrupted, just start fresh


def _save_cache(question_id: str, state: QuestionState) -> None:
    """Save cached classifications, excellent message, and summaries to file"""
    cache_file = _get_cache_file(question_id)
    try:
        # Build message summaries and classifications by message_id
        message_summaries = {}
        message_classifications_by_id = {}
        excellent_message_id = None
        
        for msg in state.discord_messages:
            if msg.two_word_summary:
                message_summaries[msg.message_id] = msg.two_word_summary
            if msg.classification:
                message_classifications_by_id[msg.message_id] = msg.classification
            if msg.is_excellent:
                excellent_message_id = msg.message_id
        
        cache_data = {
            "classifications": state.message_classifications,
            "excellent_message": state.excellent_message,
            "two_word_summaries": state.two_word_summaries,
            "message_summaries": message_summaries,
            "message_classifications_by_id": message_classifications_by_id,
            "excellent_message_id": excellent_message_id,
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    except Exception:
        pass  # Silently fail if cache can't be written


def get_question_state(question_id: str) -> Optional[QuestionState]:
    """Get question state by ID, loading cache if available"""
    state = questions.get(question_id)
    if state:
        # Load cache if not already loaded
        if not hasattr(state, '_cache_loaded'):
            _load_cache(question_id, state)
            state._cache_loaded = True
    return state


def create_question_state(question_id: str, question: str) -> QuestionState:
    """Create and store a new question state, loading cache if available"""
    state = QuestionState(
        question_id=question_id,
        question=question,
        created_at=datetime.utcnow(),
    )
    questions[question_id] = state
    
    # Load existing cache
    _load_cache(question_id, state)
    state._cache_loaded = True
    
    return state


def _auto_save_cache(question_id: str) -> None:
    """Auto-save cache after modifications"""
    state = questions.get(question_id)
    if state and hasattr(state, '_cache_loaded'):
        _save_cache(question_id, state)


async def add_message_to_question(question_id: str, message: DiscordMessage) -> None:
    """Add a Discord message to a question's state and broadcast it"""
    state = questions.get(question_id)
    if state:
        state.discord_messages.append(message)

        # Update or create participant
        if message.user_id not in state.participants:
            state.participants[message.user_id] = Participant(
                user_id=message.user_id,
                username=message.username,
                profile_pic_url=message.profile_pic_url,
            )
        state.participants[message.user_id].message_count += 1

        # Broadcast the message to all connected websocket clients
        from app.api.routes.websocket import broadcast_discord_message

        await broadcast_discord_message(
            question_id=question_id,
            username=message.username,
            message=message.content,
            profile_pic_url=message.profile_pic_url,
            message_id=message.message_id,
            user_id=message.user_id,
            timestamp=message.timestamp.isoformat() if hasattr(message.timestamp, 'isoformat') else str(message.timestamp),
            channel_id=message.channel_id,
            two_word_summary=message.two_word_summary,
            classification=message.classification,
            is_excellent=message.is_excellent,
        )


