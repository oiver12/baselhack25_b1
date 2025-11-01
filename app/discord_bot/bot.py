"""
Discord bot main class
"""
import discord
from discord.ext import commands
from app.config import settings
from app.discord_bot.commands import handle_start_discussion


class ConsensusBot(commands.Bot):
    """Discord bot for consensus building"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        """Called when bot is starting up"""
        # Register commands
        await self.add_command(self.start_discussion)
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"{self.user} has connected to Discord!")
    
    @commands.command(name="start_discussion")
    async def start_discussion(self, ctx: commands.Context, *, question: str):
        """
        Command to start a new discussion
        
        Usage: !start_discussion How should we change the room selection process?
        """
        await handle_start_discussion(ctx, question)


def create_bot() -> ConsensusBot:
    """Create and return bot instance"""
    return ConsensusBot()


async def start_bot():
    """Start the Discord bot"""
    bot = create_bot()
    await bot.start(settings.DISCORD_BOT_TOKEN)

