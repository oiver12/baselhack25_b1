"""Discord bot service for scraping messages and sending DMs."""
from typing import List, Optional
from datetime import datetime, timedelta
from app.state import DiscordMessage, Participant
from app.config import settings
import discord
from discord.ext import commands


class DiscordService:
    """Service for interacting with Discord."""
    
    def __init__(self):
        self.bot: Optional[commands.Bot] = None
    
    async def initialize_bot(self) -> None:
        """Initialize Discord bot if not already initialized."""
        if self.bot is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            
            self.bot = commands.Bot(command_prefix="!", intents=intents)
    
    async def scrape_relevant_messages(
        self, 
        question: str, 
        channel_id: Optional[int] = None,
        lookback_days: int = 30
    ) -> List[DiscordMessage]:
        """
        Scrape Discord messages relevant to the question.
        
        Args:
            question: The question to find relevant messages for
            channel_id: Specific channel ID to search, or None for all channels
            lookback_days: How many days back to search
        
        Returns:
            List of relevant Discord messages
        """
        if not self.bot:
            await self.initialize_bot()
        
        if not self.bot.is_ready():
            # Wait for bot to be ready
            await self.bot.wait_until_ready()
        
        relevant_messages: List[DiscordMessage] = []
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        # Get guild
        guild = self.bot.get_guild(settings.DISCORD_GUILD_ID) if settings.DISCORD_GUILD_ID else None
        if not guild:
            # Try to get first available guild
            if self.bot.guilds:
                guild = self.bot.guilds[0]
            else:
                return relevant_messages
        
        # Search channels
        channels = [guild.get_channel(channel_id)] if channel_id else guild.text_channels
        
        for channel in channels:
            if not channel:
                continue
            
            try:
                async for message in channel.history(limit=1000, after=cutoff_date):
                    if message.author.bot:
                        continue
                    
                    # Simple relevance check (can be enhanced with AI)
                    if self._is_message_relevant(message.content, question):
                        relevant_messages.append(
                            DiscordMessage(
                                message_id=str(message.id),
                                user_id=str(message.author.id),
                                username=message.author.name,
                                display_name=message.author.display_name or message.author.name,
                                profile_pic_url=str(message.author.display_avatar.url),
                                content=message.content,
                                timestamp=message.created_at,
                                channel_id=str(message.channel.id)
                            )
                        )
            except discord.Forbidden:
                # Skip channels we don't have access to
                continue
        
        return relevant_messages
    
    def _is_message_relevant(self, message_content: str, question: str) -> bool:
        """
        Check if a message is relevant to the question.
        Simple keyword-based check - can be enhanced with AI.
        """
        question_lower = question.lower()
        content_lower = message_content.lower()
        
        # Extract keywords from question
        keywords = [w for w in question_lower.split() if len(w) > 3]
        
        # Check if message contains any keywords
        return any(keyword in content_lower for keyword in keywords)
    
    async def send_dm_to_user(
        self, 
        user_id: int, 
        message_content: str
    ) -> bool:
        """
        Send a DM to a Discord user.
        
        Args:
            user_id: Discord user ID
            message_content: Message to send
        
        Returns:
            True if message was sent successfully
        """
        if not self.bot:
            await self.initialize_bot()
        
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message_content)
            return True
        except Exception as e:
            print(f"Error sending DM to user {user_id}: {e}")
            return False
    
    async def identify_introverted_users(
        self, 
        question_state
    ) -> List[Participant]:
        """
        Identify potentially introverted users (those who haven't participated).
        
        This is a simple heuristic - can be enhanced.
        """
        # Users with low message count or who haven't participated
        introverted = [
            participant 
            for participant in question_state.participants.values()
            if participant.message_count == 0 or participant.message_count < 2
        ]
        return introverted

