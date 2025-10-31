"""Discord bot implementation."""
import discord
from discord.ext import commands
import aiohttp
from app.config import settings
from app.state import state_manager, DiscordMessage
from app.services.summary_service import SummaryService
from app.api.routes.websocket import broadcast_bubble_update, broadcast_suggestion_update
from app.services.suggestions_service import SuggestionsService


class ConsensusBot:
    """Discord bot for collective intelligence."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.summary_service = SummaryService()
        self.suggestions_service = SuggestionsService()
        self.backend_url = f"http://localhost:{settings.PORT}"
        self._setup_commands()
        self._setup_events()
    
    def _setup_commands(self):
        """Setup bot commands."""
        
        @self.bot.command(name="start_discussion")
        async def start_discussion(ctx: commands.Context, *, question: str):
            """Start a new discussion/question."""
            if not question:
                await ctx.send("Please provide a question! Usage: `!start_discussion <question>`")
                return
            
            try:
                # Call backend API
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.backend_url}/api/questions",
                        json={"question": question}
                    ) as response:
                        if response.status == 201:
                            data = await response.json()
                            question_id = data["question_id"]
                            dashboard_url = data["dashboard_url"]
                            
                            await ctx.send(
                                f"✨ **New discussion started!**\n\n"
                                f"**Question:** {question}\n\n"
                                f"View live dashboard: {dashboard_url}"
                            )
                        else:
                            await ctx.send("❌ Failed to create discussion. Please try again.")
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")
    
    def _setup_events(self):
        """Setup bot event handlers."""
        
        @self.bot.event
        async def on_ready():
            print(f"Bot logged in as {self.bot.user}")
        
        @self.bot.event
        async def on_message(message: discord.Message):
            # Ignore bot messages
            if message.author.bot:
                await self.bot.process_commands(message)
                return
            
            # Check if this message is related to an active question
            # For now, we'll check all active questions
            for question_id, question_state in state_manager.get_all_questions().items():
                # Simple check - can be enhanced
                if self._is_message_relevant_to_question(message.content, question_state.question):
                    # Add message to state
                    discord_msg = DiscordMessage(
                        message_id=str(message.id),
                        user_id=str(message.author.id),
                        username=message.author.name,
                        display_name=message.author.display_name or message.author.name,
                        profile_pic_url=str(message.author.display_avatar.url),
                        content=message.content,
                        timestamp=message.created_at,
                        channel_id=str(message.channel.id)
                    )
                    
                    question_state.add_message(discord_msg)
                    
                    # Generate bubble (2-word summary)
                    bubble_summary = await self.summary_service.generate_two_word_summary(
                        message.content
                    )
                    bubble_data = {
                        "summary": bubble_summary,
                        "username": discord_msg.display_name,
                        "timestamp": discord_msg.timestamp.isoformat()
                    }
                    state_manager.add_bubble(question_id, bubble_data)
                    
                    # Broadcast bubble update
                    await broadcast_bubble_update(question_id, bubble_data)
                    
                    # Regenerate suggestions
                    suggestions = await self.suggestions_service.generate_suggestions(question_state)
                    state_manager.update_suggestions(question_id, suggestions)
                    
                    # Broadcast suggestion update
                    await broadcast_suggestion_update(question_id)
            
            # Process commands
            await self.bot.process_commands(message)
    
    def _is_message_relevant_to_question(self, message_content: str, question: str) -> bool:
        """Check if message is relevant to question."""
        question_lower = question.lower()
        content_lower = message_content.lower()
        
        # Extract keywords from question
        keywords = [w for w in question_lower.split() if len(w) > 3]
        
        return any(keyword in content_lower for keyword in keywords)
    
    async def start(self):
        """Start the bot."""
        await self.bot.start(settings.DISCORD_BOT_TOKEN)
    
    async def close(self):
        """Close the bot."""
        await self.bot.close()


# Global bot instance
bot_instance: ConsensusBot = None


async def get_bot() -> ConsensusBot:
    """Get or create bot instance."""
    global bot_instance
    if bot_instance is None:
        bot_instance = ConsensusBot()
    return bot_instance

