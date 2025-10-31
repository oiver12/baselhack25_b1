"""In-memory state management for questions and their data."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from app.api.schemas import Suggestion


@dataclass
class DiscordMessage:
    """Represents a Discord message."""
    message_id: str
    user_id: str
    username: str
    display_name: str
    profile_pic_url: str
    content: str
    timestamp: datetime
    channel_id: str


@dataclass
class Participant:
    """Represents a Discord participant."""
    user_id: str
    username: str
    display_name: str
    profile_pic_url: str
    message_count: int = 0
    dm_sent: bool = False
    introverted: bool = False


@dataclass
class QuestionState:
    """State for a single question/discussion session."""
    question_id: str
    question: str
    created_at: datetime
    discord_messages: List[DiscordMessage] = field(default_factory=list)
    suggestions: List[Suggestion] = field(default_factory=list)
    participants: Dict[str, Participant] = field(default_factory=dict)
    live_bubbles: List[Dict[str, str]] = field(default_factory=list)  # For 2-word summaries
    
    def add_message(self, message: DiscordMessage) -> None:
        """Add a message to the state."""
        self.discord_messages.append(message)
        
        # Update participant info
        if message.user_id not in self.participants:
            self.participants[message.user_id] = Participant(
                user_id=message.user_id,
                username=message.username,
                display_name=message.display_name,
                profile_pic_url=message.profile_pic_url
            )
        self.participants[message.user_id].message_count += 1


class StateManager:
    """Manages all question states in memory."""
    
    def __init__(self):
        self._questions: Dict[str, QuestionState] = {}
    
    def create_question(self, question: str) -> str:
        """Create a new question session and return its ID."""
        question_id = str(uuid.uuid4())
        self._questions[question_id] = QuestionState(
            question_id=question_id,
            question=question,
            created_at=datetime.now()
        )
        return question_id
    
    def get_question(self, question_id: str) -> Optional[QuestionState]:
        """Get question state by ID."""
        return self._questions.get(question_id)
    
    def update_suggestions(self, question_id: str, suggestions: List[Suggestion]) -> None:
        """Update suggestions for a question."""
        if question_id in self._questions:
            self._questions[question_id].suggestions = suggestions
    
    def add_bubble(self, question_id: str, bubble_data: Dict[str, str]) -> None:
        """Add a live bubble (2-word summary)."""
        if question_id in self._questions:
            self._questions[question_id].live_bubbles.append(bubble_data)
            # Keep only last 50 bubbles
            if len(self._questions[question_id].live_bubbles) > 50:
                self._questions[question_id].live_bubbles = self._questions[question_id].live_bubbles[-50:]
    
    def get_all_questions(self) -> Dict[str, QuestionState]:
        """Get all question states."""
        return self._questions


# Global state manager instance
state_manager = StateManager()

