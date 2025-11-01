"""
In-memory state management for questions and suggestions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from app.api.schemas import Suggestion, PersonOpinion


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
    ):
        self.message_id = message_id
        self.user_id = user_id
        self.username = username
        self.profile_pic_url = profile_pic_url
        self.content = content
        self.timestamp = timestamp
        self.channel_id = channel_id


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
        self.suggestions: List[Suggestion] = []
        self.participants: Dict[str, Participant] = {}
        # Cache for message classifications (message_content -> "good"/"neutral"/"bad")
        self.message_classifications: Dict[str, str] = {}
        # Cache for excellent message
        self.excellent_message: Optional[str] = None


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
    """Load cached classifications and excellent message from file"""
    cache_file = _get_cache_file(question_id)
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                state.message_classifications = cache_data.get("classifications", {})
                state.excellent_message = cache_data.get("excellent_message")
        except (json.JSONDecodeError, KeyError):
            pass  # If cache is corrupted, just start fresh


def _save_cache(question_id: str, state: QuestionState) -> None:
    """Save cached classifications and excellent message to file"""
    cache_file = _get_cache_file(question_id)
    try:
        cache_data = {
            "classifications": state.message_classifications,
            "excellent_message": state.excellent_message
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
        )


def update_suggestions(question_id: str, suggestions: List[Suggestion]) -> None:
    """Update suggestions for a question"""
    state = questions.get(question_id)
    if state:
        state.suggestions = suggestions
