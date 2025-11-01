"""
Discord bot main class
"""
import discord
from app.config import settings
from app.discord_bot.commands import handle_start_discussion


class ConsensusBot(discord.Client):
    """Discord bot for consensus building"""
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged on as {self.user}!')
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't respond to bot's own messages
        if message.author == self.user:
            return
        
        print(f'Message from {message.author}: {message.content}')
        
        # Check for start_discussion command
        if message.content.startswith('!start_discussion'):
            question = message.content.replace('!start_discussion', '').strip()
            if question:
                await handle_start_discussion(message, question)
            else:
                await message.reply("Please provide a question! Usage: `!start_discussion How should we change the room selection process?`")


def create_bot() -> ConsensusBot:
    """Create and return bot instance"""
    intents = discord.Intents.default()
    intents.message_content = True
    return ConsensusBot(intents=intents)


def run_bot():
    """Run the Discord bot (blocking)"""
    bot = create_bot()
    bot.run(settings.DISCORD_BOT_TOKEN)

