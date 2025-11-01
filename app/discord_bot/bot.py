"""
Discord bot main class
"""

import discord
from datetime import datetime
from typing import Dict, List, Optional
from app.config import settings
from app.state import DiscordMessage, add_message_to_active_question, get_active_question
from app.services.question_service import check_message_relevance
from app.services.pipeline import process_one

class ConsensusBot(discord.Client):
    """Discord bot for consensus building"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't respond to bot's own messages
        if message.author == self.user:
            return
        
        # Filter by channel if configured
        if settings.DISCORD_CHANNEL_ID:
            if str(message.channel.id) != settings.DISCORD_CHANNEL_ID:
                return  # Ignore messages from other channels

        print(f"Message from {message.author}: {message.content}")
        # Mark: add all messages (even those not starting with !start_discussion) to display at message endpoint
        # This ensures all messages are included in the /messages endpoint, even outside discussions
        # Create DiscordMessage object for every non-bot message and store globally

        # Get user avatar URL
        profile_pic_url = (
            message.author.display_avatar.url
            if message.author.display_avatar
            else ""
        )

        # Create DiscordMessage object (summary and classification will be set later in process_single_message_for_question)
        discord_message = DiscordMessage(
            message_id=str(message.id),
            user_id=str(message.author.id),
            username=message.author.display_name,
            profile_pic_url=profile_pic_url,
            content=message.content,
            timestamp=message.created_at or datetime.utcnow(),
            channel_id=str(message.channel.id),
        )

        # Add to global historical messages if not already present
        # Skip meta-messages like !start_discussion commands
        try:
            from app.state import (
                global_historical_messages, 
                global_historical_message_ids, 
                save_all_discord_messages,
                should_ignore_message_for_cache
            )
            if discord_message.message_id not in global_historical_message_ids:
                # Check if message should be ignored
                if not should_ignore_message_for_cache(discord_message.content, is_bot=False):
                    global_historical_messages.append(discord_message)
                    global_historical_message_ids.add(discord_message.message_id)
                    # Save to cache
                    save_all_discord_messages()
        except Exception as e:
            print(f"Warning: Could not save global message: {e}")

        # # Check for start_discussion command
        # if message.content.startswith("!start_discussion"):
        #     # Deduplication guard: prevent processing the same message twice
        #     global _processed_start_discussion_messages
        #     if message.id in _processed_start_discussion_messages:
        #         print(f"Skipping duplicate !start_discussion message: {message.id}")
        #         return  # Already processed, ignore
            
        #     # Mark as processed
        #     _processed_start_discussion_messages.add(message.id)
            
        #     question = message.content.replace("!start_discussion", "").strip()
        #     if question:
        #         await handle_start_discussion(message, question, self)
        #     else:
        #         await message.reply(
        #             "Please provide a question! Usage: `!start_discussion How should we change the room selection process?`"
        #         )
        #     return

        # Check if there's an active question
        active_question = get_active_question()
        
        if active_question:
            # Check if message is relevant to the active question
            # Uses NEW_MESSAGE_THRESHOLD by default for new incoming messages
            try:
                is_relevant = await check_message_relevance(discord_message, active_question.question)
                
                if is_relevant:
                    # Message is relevant, add to active question
                    await add_message_to_active_question(discord_message)
                    
                    # Process only this new message: generate summary, classify, update excellent status
                    try:
                        await process_one(discord_message)
                    except Exception as e:
                        print(f"Warning: Failed to process new message for active question: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    # Message is not relevant, ignore it (already saved to global cache)
                    pass
            except Exception as e:
                print(f"Warning: Failed to check message relevance: {e}")
                import traceback
                traceback.print_exc()
        else:
            # No active question, message already saved to global cache, ignore
            pass



    async def get_all_messages(self) -> List[DiscordMessage]:
        """Get all messages from the active question"""
        active_question = get_active_question()
        if active_question:
            return active_question.discord_messages
        return []


def create_bot() -> ConsensusBot:
    """Create and return bot instance"""
    intents = discord.Intents.default()
    intents.message_content = True
    return ConsensusBot(intents=intents)


# Global reference to the bot instance for accessing it from other modules
_bot_instance: Optional[ConsensusBot] = None

# Track processed !start_discussion message IDs to prevent duplicate handling
_processed_start_discussion_messages: set = set()


def get_bot_instance() -> Optional[ConsensusBot]:
    """Get the global bot instance"""
    return _bot_instance


def run_bot():
    """Run the Discord bot (blocking)"""
    global _bot_instance
    _bot_instance = create_bot()
    _bot_instance.run(settings.DISCORD_BOT_TOKEN)
