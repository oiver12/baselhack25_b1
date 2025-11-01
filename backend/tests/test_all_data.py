"""
Test file for scraping Discord history
"""
import asyncio
import sys
import threading
from pathlib import Path

# Add project root directory to path so we can import app modules
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.services.discord_service import scrape_discord_history
from app.discord_bot.bot import run_bot, get_bot_instance
from app.config import settings

async def test_scrape_discord_history():
    print("Starting Discord bot...")
    
    # Start bot in a background thread if token is available
    if not settings.DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not set in .env file")
        return
    
    # Start bot in daemon thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait for bot to be ready
    print("Waiting for bot to connect...")
    bot = get_bot_instance()
    max_wait = 30  # Wait up to 30 seconds
    for i in range(max_wait * 2):  # Check every 0.5 seconds
        await asyncio.sleep(0.5)
        bot = get_bot_instance()
        if bot and bot.is_ready():
            print(f"✓ Bot connected as {bot.user}")
            break
    else:
        print("Error: Bot failed to connect within 30 seconds")
        return
    
    # Now test scraping
    print("\nTesting scrape_discord_history...")
    messages = await scrape_discord_history()
    print(f"\nFound {len(messages)} messages:")
    for msg in messages:
        print(f"  - [{msg.username}]: {msg.content[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_scrape_discord_history())