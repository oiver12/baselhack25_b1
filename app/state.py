"""
In-memory state management for questions and messages
"""

import json
import os
from datetime import datetime, timezone
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

# Unified cache files
DISCORD_MESSAGES_CACHE = CACHE_DIR / "all_discord_messages.json"
QUESTIONS_CACHE = CACHE_DIR / "all_questions.json"


def save_all_discord_messages() -> None:
    """Save all historical Discord messages to disk"""
    global global_historical_messages
    try:
        messages_data = [
            {
                "message_id": msg.message_id,
                "user_id": msg.user_id,
                "username": msg.username,
                "profile_pic_url": msg.profile_pic_url,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp),
                "channel_id": msg.channel_id,
                "question_id": msg.question_id,
                "two_word_summary": msg.two_word_summary,
                "classification": msg.classification,
                "is_excellent": msg.is_excellent,
            }
            for msg in global_historical_messages
        ]
        with open(DISCORD_MESSAGES_CACHE, 'w') as f:
            json.dump(messages_data, f, indent=2)
        print(f"✓ Saved {len(messages_data)} Discord messages to cache")
    except Exception as e:
        print(f"Error saving Discord messages: {e}")


def load_all_discord_messages() -> None:
    """Load all historical Discord messages from disk"""
    global global_historical_messages, global_historical_message_ids
    if not DISCORD_MESSAGES_CACHE.exists():
        return
    
    try:
        with open(DISCORD_MESSAGES_CACHE, 'r') as f:
            messages_data = json.load(f)
        
        global_historical_messages.clear()
        global_historical_message_ids.clear()
        
        for msg_data in messages_data:
            msg = DiscordMessage(
                message_id=msg_data["message_id"],
                user_id=msg_data["user_id"],
                username=msg_data["username"],
                profile_pic_url=msg_data["profile_pic_url"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                channel_id=msg_data["channel_id"],
                question_id=msg_data.get("question_id"),
                two_word_summary=msg_data.get("two_word_summary"),
                classification=msg_data.get("classification"),
                is_excellent=msg_data.get("is_excellent", False),
            )
            global_historical_messages.append(msg)
            global_historical_message_ids.add(msg.message_id)
        
        print(f"✓ Loaded {len(global_historical_messages)} Discord messages from cache")
    except Exception as e:
        print(f"Error loading Discord messages: {e}")


def save_all_questions() -> None:
    """Save all question states to disk"""
    try:
        questions_data = {}
        for qid, state in questions.items():
            questions_data[qid] = {
                "question_id": state.question_id,
                "question": state.question,
                "created_at": state.created_at.isoformat(),
                "discord_messages": [
                    {
                        "message_id": msg.message_id,
                        "user_id": msg.user_id,
                        "username": msg.username,
                        "profile_pic_url": msg.profile_pic_url,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp),
                        "channel_id": msg.channel_id,
                        "question_id": msg.question_id,
                        "two_word_summary": msg.two_word_summary,
                        "classification": msg.classification,
                        "is_excellent": msg.is_excellent,
                    }
                    for msg in state.discord_messages
                ],
                "participants": {
                    pid: {
                        "user_id": p.user_id,
                        "username": p.username,
                        "profile_pic_url": p.profile_pic_url,
                        "message_count": p.message_count,
                        "dm_sent": p.dm_sent,
                    }
                    for pid, p in state.participants.items()
                },
                "two_word_summaries": state.two_word_summaries,
                "message_classifications": state.message_classifications,
                "excellent_message": state.excellent_message,
            }
        
        with open(QUESTIONS_CACHE, 'w') as f:
            json.dump(questions_data, f, indent=2)
        print(f"✓ Saved {len(questions_data)} questions to cache")
    except Exception as e:
        print(f"Error saving questions: {e}")


def load_all_questions() -> None:
    """Load all question states from disk"""
    if not QUESTIONS_CACHE.exists():
        return
    
    try:
        with open(QUESTIONS_CACHE, 'r') as f:
            questions_data = json.load(f)
        
        for qid, data in questions_data.items():
            # Create question state
            state = QuestionState(
                question_id=data["question_id"],
                question=data["question"],
                created_at=datetime.fromisoformat(data["created_at"]),
            )
            
            # Restore messages
            for msg_data in data.get("discord_messages", []):
                msg = DiscordMessage(
                    message_id=msg_data["message_id"],
                    user_id=msg_data["user_id"],
                    username=msg_data["username"],
                    profile_pic_url=msg_data["profile_pic_url"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    channel_id=msg_data["channel_id"],
                    question_id=msg_data.get("question_id"),
                    two_word_summary=msg_data.get("two_word_summary"),
                    classification=msg_data.get("classification"),
                    is_excellent=msg_data.get("is_excellent", False),
                )
                state.discord_messages.append(msg)
            
            # Restore participants
            for pid, p_data in data.get("participants", {}).items():
                state.participants[pid] = Participant(
                    user_id=p_data["user_id"],
                    username=p_data["username"],
                    profile_pic_url=p_data["profile_pic_url"],
                    message_count=p_data.get("message_count", 0),
                    dm_sent=p_data.get("dm_sent", False),
                )
            
            state.two_word_summaries = data.get("two_word_summaries", [])
            state.message_classifications = data.get("message_classifications", {})
            state.excellent_message = data.get("excellent_message")
            
            questions[qid] = state
        
        print(f"✓ Loaded {len(questions_data)} questions from cache")
    except Exception as e:
        print(f"Error loading questions: {e}")


def get_newest_cached_message_timestamp() -> Optional[datetime]:
    """Get the timestamp of the newest cached message"""
    global global_historical_messages
    
    if not global_historical_messages:
        return None
    
    # Normalize timestamps - convert timezone-aware to naive for comparison
    def normalize_timestamp(dt: datetime) -> datetime:
        if dt.tzinfo is not None:
            # Convert to UTC then remove timezone info
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    
    # Find message with latest timestamp (normalized)
    newest = max(
        global_historical_messages, 
        key=lambda m: normalize_timestamp(m.timestamp)
    )
    return normalize_timestamp(newest.timestamp)


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
        
        # Auto-save all caches
        save_all_discord_messages()
        save_all_questions()


