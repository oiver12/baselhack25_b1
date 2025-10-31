"""Service for generating summaries and classifications."""
from typing import Literal
from app.config import settings


class SummaryService:
    """Service for generating 2-word summaries and classifications."""
    
    async def generate_two_word_summary(self, message: str) -> str:
        """
        Generate a 2-word summary of a message.
        
        Args:
            message: The message content
        
        Returns:
            Two-word summary
        """
        # Simple extraction - first two significant words
        # In production, use OpenAI or similar for better summaries
        words = message.split()
        significant_words = [w.strip(".,!?;:") for w in words if len(w) > 3][:2]
        
        if len(significant_words) < 2:
            # Fallback: use first two words
            words = message.split()[:2]
            significant_words = [w.strip(".,!?;:") for w in words]
        
        return " ".join(significant_words[:2])
    
    async def classify_message(
        self, 
        message: str
    ) -> Literal["sophisticated", "simple", "neutral"]:
        """
        Classify a message as sophisticated, simple, or neutral.
        
        Args:
            message: The message content
        
        Returns:
            Classification type
        """
        # Simple heuristic - can be enhanced with AI
        message_lower = message.lower()
        word_count = len(message.split())
        
        # Sophisticated indicators
        sophisticated_words = ["analyze", "consider", "propose", "suggest", "evaluate", 
                             "implications", "however", "therefore", "furthermore"]
        
        # Simple indicators
        simple_words = ["yes", "no", "ok", "sure", "maybe", "idk", "i think"]
        
        sophisticated_count = sum(1 for word in sophisticated_words if word in message_lower)
        simple_count = sum(1 for word in simple_words if word in message_lower)
        
        if word_count > 30 or sophisticated_count >= 2:
            return "sophisticated"
        elif simple_count >= 1 or word_count < 5:
            return "simple"
        else:
            return "neutral"
    
    async def summarize_multiple_messages(self, messages: list[str]) -> str:
        """
        Summarize multiple messages (for DM follow-ups).
        
        Args:
            messages: List of message contents
        
        Returns:
            Summary text
        """
        # Simple concatenation - in production, use AI for better summarization
        if not messages:
            return ""
        
        if len(messages) == 1:
            return messages[0]
        
        # Combine messages with newlines
        return "\n".join(f"- {msg}" for msg in messages)

