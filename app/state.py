"""
In-memory state management for questions and messages
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
from uuid import uuid4


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


def should_ignore_message_for_cache(message_content: str, user_id: Optional[str] = None, is_bot: bool = False) -> bool:
    """
    Check if a message should be ignored for caching and analysis.
    
    Ignores:
    - !start_discussion command messages
    - Bot messages (already filtered elsewhere, but double-check)
    
    Args:
        message_content: The message content
        user_id: Optional user ID (for future filtering if needed)
        is_bot: Whether the message is from a bot
        
    Returns:
        True if message should be ignored, False otherwise
    """
    # Ignore bot messages
    if is_bot:
        return True
    
    # Ignore !start_discussion commands
    if message_content.startswith("!start_discussion"):
        return True
    
    return False


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


class Cluster:
    """Represents a message cluster with centroid and metrics"""
    
    def __init__(
        self,
        cluster_id: str,
        label: str,
        centroid: List[float],
        message_ids: List[str],
        frozen: bool = False,
        intra_sim: float = 0.0,
        sentiment_avg: float = 0.0,
        sentiment_std: float = 0.0,
        created_at: Optional[datetime] = None,
    ):
        self.cluster_id = cluster_id
        self.label = label
        self.centroid = centroid  # List[float] for serialization
        self.message_ids = message_ids
        self.frozen = frozen
        self.intra_sim = intra_sim
        self.sentiment_avg = sentiment_avg
        self.sentiment_std = sentiment_std
        self.created_at = created_at or datetime.utcnow()


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
        # Clusters with centroids and metrics
        self.clusters: List[Cluster] = []
        # Unassigned message IDs awaiting cluster assignment
        self.unassigned_buffer: List[str] = []


# Global in-memory storage
active_question: Optional[QuestionState] = None

# Global storage for all historical Discord messages (fetched once on startup)
global_historical_messages: List[DiscordMessage] = []

# Set cache for efficient duplicate checking of message IDs
global_historical_message_ids: set = set()

# Cache directory for persistent storage
CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)

# Unified cache files
DISCORD_MESSAGES_CACHE = CACHE_DIR / "all_discord_messages.json"
ACTIVE_QUESTION_CACHE = CACHE_DIR / "active_question.json"
QUESTIONS_CACHE = CACHE_DIR / "all_questions.json"  # Legacy, for migration


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
    """Save active question to disk"""
    global active_question
    try:
        if active_question:
            question_data = {
                "question_id": active_question.question_id,
                "question": active_question.question,
                "created_at": active_question.created_at.isoformat(),
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
                    for msg in active_question.discord_messages
                ],
                "participants": {
                    pid: {
                        "user_id": p.user_id,
                        "username": p.username,
                        "profile_pic_url": p.profile_pic_url,
                        "message_count": p.message_count,
                        "dm_sent": p.dm_sent,
                    }
                    for pid, p in active_question.participants.items()
                },
                "two_word_summaries": active_question.two_word_summaries,
                "message_classifications": active_question.message_classifications,
                "excellent_message": active_question.excellent_message,
                "clusters": [
                    {
                        "cluster_id": c.cluster_id,
                        "label": c.label,
                        "centroid": c.centroid,  # Already List[float]
                        "message_ids": c.message_ids,
                        "frozen": c.frozen,
                        "intra_sim": c.intra_sim,
                        "sentiment_avg": c.sentiment_avg,
                        "sentiment_std": c.sentiment_std,
                        "created_at": c.created_at.isoformat() if hasattr(c.created_at, 'isoformat') else str(c.created_at),
                    }
                    for c in active_question.clusters
                ],
                "unassigned_buffer": active_question.unassigned_buffer,
            }
            cache_data = {"active_question": question_data}
        else:
            cache_data = {"active_question": None}
        
        with open(ACTIVE_QUESTION_CACHE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        if active_question:
            print(f"✓ Saved active question to cache")
        else:
            print(f"✓ Saved empty active question state to cache")
    except Exception as e:
        print(f"Error saving active question: {e}")


def load_all_questions() -> None:
    """Load active question from disk, with migration from old format"""
    global active_question
    
    # Try new format first
    if ACTIVE_QUESTION_CACHE.exists():
        try:
            with open(ACTIVE_QUESTION_CACHE, 'r') as f:
                cache_data = json.load(f)
            
            question_data = cache_data.get("active_question")
            if question_data:
                # Restore active question
                state = QuestionState(
                    question_id=question_data["question_id"],
                    question=question_data["question"],
                    created_at=datetime.fromisoformat(question_data["created_at"]),
                )
                
                # Restore messages
                for msg_data in question_data.get("discord_messages", []):
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
                for pid, p_data in question_data.get("participants", {}).items():
                    state.participants[pid] = Participant(
                        user_id=p_data["user_id"],
                        username=p_data["username"],
                        profile_pic_url=p_data["profile_pic_url"],
                        message_count=p_data.get("message_count", 0),
                        dm_sent=p_data.get("dm_sent", False),
                    )
                
                state.two_word_summaries = question_data.get("two_word_summaries", [])
                state.message_classifications = question_data.get("message_classifications", {})
                state.excellent_message = question_data.get("excellent_message")
                
                # Restore clusters
                clusters_data = question_data.get("clusters", [])
                for c_data in clusters_data:
                    cluster = Cluster(
                        cluster_id=c_data["cluster_id"],
                        label=c_data["label"],
                        centroid=c_data["centroid"],  # Already List[float]
                        message_ids=c_data["message_ids"],
                        frozen=c_data.get("frozen", False),
                        intra_sim=c_data.get("intra_sim", 0.0),
                        sentiment_avg=c_data.get("sentiment_avg", 0.0),
                        sentiment_std=c_data.get("sentiment_std", 0.0),
                        created_at=datetime.fromisoformat(c_data["created_at"]) if c_data.get("created_at") else None,
                    )
                    state.clusters.append(cluster)
                
                # Restore unassigned buffer
                state.unassigned_buffer = question_data.get("unassigned_buffer", [])
                
                active_question = state
                print(f"✓ Loaded active question from cache")
                return
        except Exception as e:
            print(f"Error loading active question from new format: {e}")
    
    # Migration: Try old format and convert
    if QUESTIONS_CACHE.exists():
        try:
            with open(QUESTIONS_CACHE, 'r') as f:
                questions_data = json.load(f)
            
            if questions_data:
                # Take the most recent question (by created_at) or first one
                most_recent = None
                most_recent_time = None
                
                for qid, data in questions_data.items():
                    created_at = datetime.fromisoformat(data["created_at"])
                    if most_recent is None or created_at > most_recent_time:
                        most_recent = (qid, data)
                        most_recent_time = created_at
                
                if most_recent:
                    qid, data = most_recent
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
                    
                    # Initialize empty clusters and buffer (will be bootstrapped later)
                    state.clusters = []
                    state.unassigned_buffer = []
                    
                    active_question = state
                    # Save in new format
                    save_all_questions()
                    print(f"✓ Migrated question from old format to active question")
                    return
        except Exception as e:
            print(f"Error loading/migrating from old format: {e}")


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


def get_active_question() -> Optional[QuestionState]:
    """Get the active question state"""
    return active_question


def get_question_state(question_id: str) -> Optional[QuestionState]:
    """Get question state by ID (legacy function - checks active_question)"""
    global active_question
    if active_question and active_question.question_id == question_id:
        return active_question
    return None


def create_question_state(question_id: str, question: str) -> QuestionState:
    """Create and store a new active question state (replaces any existing)"""
    global active_question
    state = QuestionState(
        question_id=question_id,
        question=question,
        created_at=datetime.utcnow(),
    )
    active_question = state
    return state


async def add_message_to_active_question(message: DiscordMessage) -> None:
    """Add a Discord message to the active question's state and broadcast it"""
    global active_question
    if not active_question:
        return
    
    # Set question_id on message
    message.question_id = active_question.question_id
    
    # Check if message already exists (avoid duplicates)
    if any(m.message_id == message.message_id for m in active_question.discord_messages):
        return
    
    active_question.discord_messages.append(message)

    # Update or create participant
    if message.user_id not in active_question.participants:
        active_question.participants[message.user_id] = Participant(
            user_id=message.user_id,
            username=message.username,
            profile_pic_url=message.profile_pic_url,
        )
    active_question.participants[message.user_id].message_count += 1

    # Broadcast the message to all connected websocket clients
    from app.api.routes.websocket import broadcast_discord_message

    await broadcast_discord_message(
        question_id=active_question.question_id,
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


async def add_message_to_question(question_id: str, message: DiscordMessage) -> None:
    """Legacy function - redirects to add_message_to_active_question if question_id matches"""
    global active_question
    if active_question and active_question.question_id == question_id:
        await add_message_to_active_question(message)


