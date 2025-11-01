"""
Test file for get_whole_Report - simple test with Discord data
"""
import asyncio
import sys
import threading
import json
from pathlib import Path

# Add project root directory to path so we can import app modules
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.services.report import get_whole_Report
from app.services.discord_service import scrape_discord_history
from app.discord_bot.bot import run_bot, get_bot_instance
from app.config import settings
from app.state import create_question_state, Participant


async def wait_for_bot(max_wait: int = 30):
    """Wait for bot to be ready"""
    print("Waiting for bot to connect...")
    for i in range(max_wait * 2):
        await asyncio.sleep(0.5)
        bot = get_bot_instance()
        if bot and bot.is_ready():
            print(f"✓ Bot connected")
            return bot
    print("Error: Bot failed to connect")
    return None


async def main():
    """Test get_whole_Report with Discord data"""
    if not settings.DISCORD_BOT_TOKEN:
        print("⚠ Error: DISCORD_BOT_TOKEN not set")
        return
    
    # Start bot
    print("Starting Discord bot...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait for bot
    bot = await wait_for_bot()
    if not bot:
        return
    
    # Fetch messages from Discord
    print("Fetching messages from Discord...")
    messages = await scrape_discord_history()
    print(f"Found {len(messages)} messages")
    
    if len(messages) == 0:
        print("⚠ No messages found")
        return
    
    # Create question state with all messages
    from uuid import uuid4
    question_state = create_question_state(str(uuid4()), "Test Question")
    
    for msg in messages:
        msg.question_id = question_state.question_id
        if not any(m.message_id == msg.message_id for m in question_state.discord_messages):
            question_state.discord_messages.append(msg)
            if msg.user_id not in question_state.participants:
                question_state.participants[msg.user_id] = Participant(
                    user_id=msg.user_id,
                    username=msg.username,
                    profile_pic_url=msg.profile_pic_url,
                )
            question_state.participants[msg.user_id].message_count += 1
    
    print(f"Question has {len(question_state.discord_messages)} messages")
    
    # Run get_whole_Report
    print("\nRunning get_whole_Report...")
    report = await get_whole_Report(question_state)
    
    results = report.get("results", [])
    summary = report.get("summary", {})
    
    print(f"\n✓ Report complete - {len(results)} results")
    print(f"\nSummary:")
    if isinstance(summary, dict):
        print(json.dumps(summary, indent=2))
    else:
        print(summary)
    
    print(f"\nFirst few coordinates:")
    for r in results[:5]:
        print(f"  {r['message_id'][:20]}...: ({r['x']:.3f}, {r['y']:.3f})")


if __name__ == "__main__":
    asyncio.run(main())
