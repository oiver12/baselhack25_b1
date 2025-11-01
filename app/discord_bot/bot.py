"""
Discord bot main class
"""

import discord
from datetime import datetime
from typing import Dict
from app.config import settings
from app.discord_bot.commands import handle_start_discussion
from app.state import DiscordMessage, add_message_to_question


class ConsensusBot(discord.Client):
    """Discord bot for consensus building"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Map channel_id -> question_id for active discussions
        self.active_discussions: Dict[str, str] = {}

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't respond to bot's own messages
        if message.author == self.user:
            return

        print(f"Message from {message.author}: {message.content}")

        # Check for start_discussion command
        if message.content.startswith("!start_discussion"):
            question = message.content.replace("!start_discussion", "").strip()
            if question:
                await handle_start_discussion(message, question, self)
            else:
                await message.reply(
                    "Please provide a question! Usage: `!start_discussion How should we change the room selection process?`"
                )
            return

        # Forward messages from active discussion channels
        channel_id = str(message.channel.id)
        if channel_id in self.active_discussions:
            question_id = self.active_discussions[channel_id]

            # Get user avatar URL
            profile_pic_url = (
                message.author.display_avatar.url
                if message.author.display_avatar
                else ""
            )

            # Create DiscordMessage object
            discord_message = DiscordMessage(
                message_id=str(message.id),
                user_id=str(message.author.id),
                username=message.author.display_name,
                profile_pic_url=profile_pic_url,
                content=message.content,
                timestamp=message.created_at or datetime.utcnow(),
                channel_id=channel_id,
            )

            # Add message to question state (this will also broadcast it)
            await add_message_to_question(question_id, discord_message)


def create_bot() -> ConsensusBot:
    """Create and return bot instance"""
    intents = discord.Intents.default()
    intents.message_content = True
    return ConsensusBot(intents=intents)


def run_bot():
    """Run the Discord bot (blocking)"""
    bot = create_bot()
    bot.run(settings.DISCORD_BOT_TOKEN)
