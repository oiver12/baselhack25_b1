"""
Discord service for scraping messages and sending DMs
"""
import discord
from datetime import datetime, timedelta
from typing import List, Optional
from app.state import DiscordMessage, get_question_state
from app.config import settings
from app.discord_bot.bot import get_bot_instance


async def scrape_discord_history(after: Optional[datetime] = None) -> List[DiscordMessage]:
    """
    Scrape Discord chat history for all messages
    
    Args:
        after: Optional datetime - only fetch messages newer than this timestamp
               If None, performs full scrape of all messages
    
    Returns:
        List of all Discord messages
    """
    messages: List[DiscordMessage] = []
    
    # Get bot instance
    bot = get_bot_instance()
    if not bot:
        print("Warning: Bot instance not available for scraping history")
        return messages
    
    # Wait for bot to be ready if it's still connecting
    if not bot.is_ready():
        print("Waiting for bot to be ready...")
        # Wait up to 10 seconds for bot to be ready
        import asyncio
        for _ in range(20):  # 20 * 0.5s = 10s
            await asyncio.sleep(0.5)
            if bot.is_ready():
                break
        else:
            print("Warning: Bot not ready after waiting, skipping history scrape")
            return messages
    
    # Get bot's event loop - bot runs in a separate thread with its own loop
    import asyncio
    bot_loop = bot.loop
    
    # If we're not in the bot's loop, we need to run in that loop
    current_loop = asyncio.get_event_loop()
    if bot_loop != current_loop:
        # Run the actual scraping in the bot's loop using run_coroutine_threadsafe
        async def _scrape_in_bot_loop():
            return await _do_scrape(bot, after=after)
        
        import concurrent.futures
        future = asyncio.run_coroutine_threadsafe(_scrape_in_bot_loop(), bot_loop)
        messages = future.result(timeout=300)  # 5 minute timeout
        return messages
    else:
        # We're already in the bot's loop, just do it directly
        return await _do_scrape(bot, after=after)


async def _do_scrape(bot, after: Optional[datetime] = None) -> List[DiscordMessage]:
    """
    Internal function to do the actual scraping - runs in bot's event loop
    
    Args:
        bot: Discord bot instance
        after: Optional datetime - only fetch messages newer than this timestamp
    """
    messages: List[DiscordMessage] = []
    
    # Log scraping mode
    if after:
        print(f"Scraping mode: INCREMENTAL (messages after {after.isoformat()})")
    else:
        print(f"Scraping mode: FULL (all messages)")
    
    # Get guild - try from settings first, otherwise use the first available guild
    guild = None
    guild_id = settings.DISCORD_GUILD_ID
    if guild_id:
        try:
            guild = bot.get_guild(int(guild_id))
            if not guild:
                print(f"Warning: Guild {guild_id} from settings not found, trying to find any available guild...")
        except ValueError:
            print(f"Warning: Invalid DISCORD_GUILD_ID format, trying to find any available guild...")
    
    # If no guild found from settings, try to get the first available guild
    if not guild:
        if bot.guilds:
            guild = bot.guilds[0]
            print(f"Using first available guild: {guild.name} (ID: {guild.id})")
        else:
            print("Error: No guilds available for the bot")
            return messages
    
    try:
        # Get specific channel if configured, otherwise use all channels
        target_channel_id = settings.DISCORD_CHANNEL_ID
        channels_to_search = []
        
        if target_channel_id:
            # Only use the specified channel
            try:
                channel = bot.get_channel(int(target_channel_id))
                if channel and channel.guild == guild:
                    channels_to_search = [channel]
                    print(f"Using specific channel: #{channel.name} (ID: {target_channel_id})")
                else:
                    print(f"Warning: Channel {target_channel_id} not found or not in this guild")
                    return messages
            except ValueError:
                print(f"Warning: Invalid DISCORD_CHANNEL_ID format")
                return messages
        else:
            # Use all text channels (current behavior)
            channels_to_search = guild.text_channels
            print(f"Searching {len(channels_to_search)} text channels for messages...")
        
        for channel in channels_to_search:
            try:
                # Check if bot has permission to read message history
                if not channel.permissions_for(guild.me).read_message_history:
                    print(f"  Skipping #{channel.name}: no read permission")
                    continue
                
                if after:
                    print(f"  Fetching NEW messages from #{channel.name} (after {after.isoformat()})...")
                else:
                    print(f"  Fetching ALL messages from #{channel.name}...")
                
                # Fetch messages from channel history
                channel_messages = []
                
                # Fetch messages in batches to avoid timeout issues
                # Discord API allows fetching up to 100 messages at a time
                batch_count = 0
                last_message_id = None
                
                while True:
                    try:
                        # Fetch up to 100 messages at a time
                        fetch_limit = 100
                        fetched = []
                        
                        # Create async iterator for history
                        # Wrap in a task to ensure proper context
                        import asyncio
                        
                        async def fetch_batch():
                            msgs = []
                            if after:
                                # Incremental mode: only fetch messages after the timestamp
                                async for msg in channel.history(
                                    limit=fetch_limit,
                                    after=after,
                                    oldest_first=False  # Most recent first
                                ):
                                    msgs.append(msg)
                                # For incremental, we typically only need one batch
                                # Stop after first batch in incremental mode
                            elif last_message_id:
                                # Full scrape: Fetch messages before the last one we got
                                async for msg in channel.history(
                                    limit=fetch_limit,
                                    before=discord.Object(id=last_message_id),
                                    oldest_first=False
                                ):
                                    msgs.append(msg)
                            else:
                                # First batch - fetch most recent messages
                                async for msg in channel.history(
                                    limit=fetch_limit,
                                    oldest_first=False
                                ):
                                    msgs.append(msg)
                            return msgs
                        
                        # Create task to ensure proper async context
                        task = asyncio.create_task(fetch_batch())
                        fetched = await task
                        
                        if not fetched:
                            break
                        
                        # Process fetched messages
                        for message in fetched:
                            # Skip bot messages
                            if message.author.bot:
                                continue
                            
                            # Skip empty messages
                            if not message.content.strip():
                                continue
                            
                            # Skip !start_discussion command messages
                            if message.content.startswith("!start_discussion"):
                                continue
                            
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
                                username=message.author.display_name or message.author.name,
                                profile_pic_url=profile_pic_url,
                                content=message.content,
                                timestamp=message.created_at.replace(tzinfo=None) if message.created_at else datetime.utcnow(),
                                channel_id=str(channel.id),
                            )
                            channel_messages.append(discord_message)
                        
                        # Update last_message_id for next batch (only for full scrape)
                        if not after:
                            last_message_id = fetched[-1].id
                            batch_count += 1
                            
                            print(f"    Batch {batch_count}: {len(fetched)} messages (total in channel: {len(channel_messages)})")
                            
                            # If we got fewer than the limit, we've reached the end
                            if len(fetched) < fetch_limit:
                                break
                        else:
                            # Incremental mode: only one batch needed
                            batch_count = 1
                            print(f"    Found {len(fetched)} new messages in #{channel.name}")
                            break
                    
                    except Exception as e:
                        print(f"    Error in batch {batch_count + 1} for #{channel.name}: {e}")
                        import traceback
                        traceback.print_exc()
                        # Try to continue with next batch if possible
                        if last_message_id:
                            # Try next batch with a small delay
                            import asyncio
                            await asyncio.sleep(0.5)
                            continue
                        else:
                            # If we can't even get the first batch, break
                            break
                
                messages.extend(channel_messages)
                if channel_messages:
                    print(f"  Found {len(channel_messages)} messages in #{channel.name}")
                else:
                    print(f"  No messages found in #{channel.name}")
            
            except discord.Forbidden:
                # Bot doesn't have permission to read this channel
                print(f"  Skipping #{channel.name}: forbidden")
                continue
            except Exception as e:
                print(f"  Error fetching messages from channel {channel.name}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if after:
            print(f"\nINCREMENTAL scrape complete: Found {len(messages)} NEW messages across all channels")
        else:
            print(f"\nFULL scrape complete: Found {len(messages)} total messages across all channels")
        
        # Sort by timestamp (oldest first)
        messages.sort(key=lambda x: x.timestamp)
        
    except Exception as e:
        print(f"Error scraping Discord history: {e}")
        import traceback
        traceback.print_exc()
    
    return messages


async def send_dm_to_introverted_users(question_id: str, question: str) -> None:
    """
    Send DMs to introverted users asking for their views
    
    Args:
        question_id: The question ID
        question: The question text
    """
    # TODO: Implement DM sending logic
    # - Identify introverted users (based on message frequency, etc.)
    # - Send DM with question and link to dashboard
    # - Track which users received DMs in question state
    
    question_state = get_question_state(question_id)
    if question_state:
        # Mark participants as DM sent
        pass


async def listen_for_new_messages(question_id: str) -> None:
    """
    Listen for new Discord messages related to a question
    
    Args:
        question_id: The question ID to listen for
    """
    # TODO: Implement Discord event listener
    # - Listen to Discord channel for new messages
    # - Filter for relevance to question
    # - Process and add to question state
    
    pass


async def get_user_profile(user_id: str) -> dict:
    """
    Get Discord user profile information
    
    Args:
        user_id: Discord user ID
        
    Returns:
        Dictionary with username, profile_pic_url, etc.
    """
    # TODO: Implement user profile fetching
    # - Fetch user info from Discord API
    # - Return username, avatar URL, etc.
    
    return {
        "username": "",
        "profile_pic_url": "",
    }

