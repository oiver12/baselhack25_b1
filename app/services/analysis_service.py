"""Service for analyzing messages and extracting insights."""
from typing import List, Tuple
from app.state import DiscordMessage


class AnalysisService:
    """Service for analyzing Discord messages."""
    
    async def extract_pros_and_cons(self, messages: List[DiscordMessage]) -> Tuple[List[str], List[str]]:
        """
        Extract pros and cons from messages.
        
        Args:
            messages: List of Discord messages
        
        Returns:
            Tuple of (pros, cons) lists
        """
        pros = []
        cons = []
        
        positive_indicators = ["good", "great", "like", "love", "benefit", "advantage", 
                              "pro", "yes", "support", "agree", "works", "helpful"]
        negative_indicators = ["bad", "hate", "problem", "issue", "worry", "concern",
                              "against", "no", "disagree", "doesn't work", "difficult"]
        
        for msg in messages:
            content_lower = msg.content.lower()
            
            # Simple extraction based on keywords
            if any(indicator in content_lower for indicator in positive_indicators):
                # Extract the positive aspect
                for sentence in msg.content.split("."):
                    sentence_lower = sentence.lower()
                    if any(indicator in sentence_lower for indicator in positive_indicators):
                        pros.append(sentence.strip())
            
            if any(indicator in content_lower for indicator in negative_indicators):
                for sentence in msg.content.split("."):
                    sentence_lower = sentence.lower()
                    if any(indicator in sentence_lower for indicator in negative_indicators):
                        cons.append(sentence.strip())
        
        # Deduplicate and limit
        pros = list(set(pros))[:10]
        cons = list(set(cons))[:10]
        
        return pros, cons
    
    async def cluster_messages_by_theme(self, messages: List[DiscordMessage]) -> List[Tuple[str, List[DiscordMessage]]]:
        """
        Cluster messages by theme/topic.
        
        Args:
            messages: List of Discord messages
        
        Returns:
            List of (theme_title, messages) tuples
        """
        # Simple keyword-based clustering
        # In production, use NLP/ML for better clustering
        
        themes: dict[str, List[DiscordMessage]] = {}
        
        # Common themes/keywords
        theme_keywords = {
            "voting": ["vote", "voting", "poll", "election", "democratic"],
            "first_come": ["first", "fifo", "queue", "early", "signup"],
            "lottery": ["lottery", "random", "draw", "chance"],
            "assigned": ["assign", "allocate", "committee", "manual"],
            "merit": ["merit", "performance", "grades", "achievement"]
        }
        
        for msg in messages:
            content_lower = msg.content.lower()
            matched_theme = None
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    matched_theme = theme.replace("_", " ").title()
                    break
            
            if not matched_theme:
                matched_theme = "Other Suggestions"
            
            if matched_theme not in themes:
                themes[matched_theme] = []
            themes[matched_theme].append(msg)
        
        return [(theme, msgs) for theme, msgs in themes.items() if msgs]

