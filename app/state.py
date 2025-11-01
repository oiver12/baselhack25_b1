"""
In-memory state management for questions and suggestions
"""
from datetime import datetime
from typing import Dict, List, Optional
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


# Global in-memory storage
questions: Dict[str, QuestionState] = {}


def get_question_state(question_id: str) -> Optional[QuestionState]:
    """Get question state by ID"""
    return questions.get(question_id)


def create_question_state(question_id: str, question: str) -> QuestionState:
    """Create and store a new question state"""
    state = QuestionState(
        question_id=question_id,
        question=question,
        created_at=datetime.utcnow(),
    )
    questions[question_id] = state
    return state


def add_message_to_question(question_id: str, message: DiscordMessage) -> None:
    """Add a Discord message to a question's state"""
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


def update_suggestions(question_id: str, suggestions: List[Suggestion]) -> None:
    """Update suggestions for a question"""
    state = questions.get(question_id)
    if state:
        state.suggestions = suggestions

