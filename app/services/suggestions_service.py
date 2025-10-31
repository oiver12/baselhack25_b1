"""Service for generating Suggestions from messages."""
from typing import List
from app.state import QuestionState, DiscordMessage, Participant
from app.api.schemas import Suggestion, PersonOpinion
from app.services.analysis_service import AnalysisService
from app.services.summary_service import SummaryService


class SuggestionsService:
    """Service for generating Suggestions matching the TypeScript type."""
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.summary_service = SummaryService()
    
    async def generate_suggestions(self, question_state: QuestionState) -> List[Suggestion]:
        """
        Generate Suggestions from the question state.
        
        Args:
            question_state: The state containing messages and participants
        
        Returns:
            List of Suggestion objects matching the TypeScript type
        """
        if not question_state.discord_messages:
            return []
        
        # Cluster messages by theme
        theme_clusters = await self.analysis_service.cluster_messages_by_theme(
            question_state.discord_messages
        )
        
        suggestions: List[Suggestion] = []
        total_messages = len(question_state.discord_messages)
        
        for theme_title, theme_messages in theme_clusters:
            # Calculate size (0-1) based on message count
            size = len(theme_messages) / total_messages if total_messages > 0 else 0
            
            # Extract pros and cons
            pros, cons = await self.analysis_service.extract_pros_and_cons(theme_messages)
            
            # Build people_opinions
            people_opinions: List[PersonOpinion] = []
            
            # Group messages by user
            user_messages: dict[str, List[DiscordMessage]] = {}
            for msg in theme_messages:
                if msg.user_id not in user_messages:
                    user_messages[msg.user_id] = []
                user_messages[msg.user_id].append(msg)
            
            for user_id, messages in user_messages.items():
                # Get participant info
                participant = question_state.participants.get(user_id)
                if not participant:
                    # Create participant from first message
                    first_msg = messages[0]
                    participant = Participant(
                        user_id=first_msg.user_id,
                        username=first_msg.username,
                        display_name=first_msg.display_name,
                        profile_pic_url=first_msg.profile_pic_url
                    )
                
                # Combine messages if multiple
                if len(messages) == 1:
                    message_text = messages[0].content
                else:
                    # Summarize multiple messages
                    message_text = await self.summary_service.summarize_multiple_messages(
                        [msg.content for msg in messages]
                    )
                
                # Classify message
                classification = await self.summary_service.classify_message(message_text)
                
                people_opinions.append(
                    PersonOpinion(
                        name=participant.display_name,
                        profile_pic_url=participant.profile_pic_url,
                        message=message_text,
                        classification=classification
                    )
                )
            
            suggestions.append(
                Suggestion(
                    title=theme_title,
                    size=min(size, 1.0),  # Ensure it's 0-1
                    pros=pros[:5],  # Limit pros
                    contra=cons[:5],  # Limit cons
                    people_opinions=people_opinions
                )
            )
        
        # Sort by size (largest first)
        suggestions.sort(key=lambda x: x.size, reverse=True)
        
        return suggestions

