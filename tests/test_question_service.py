"""
Test file for question_service - using real Discord messages
"""
import asyncio
import sys
import threading
from pathlib import Path

# Add project root directory to path so we can import app modules
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.services.question_service import assign_messages_to_existing_questions
from app.services.discord_service import scrape_discord_history
from app.discord_bot.bot import run_bot, get_bot_instance
from app.config import settings
from app.state import questions

async def test_extract_and_assign_messages():
    """Test extracting questions from real Discord messages"""
    print("=" * 80)
    print("Testing assign_messages_to_existing_questions with real Discord messages")
    print("=" * 80)
    
    # Start bot if not already running
    print("\n[1/4] Starting Discord bot...")
    bot = get_bot_instance()
    if not bot or not bot.is_ready():
        if not settings.DISCORD_BOT_TOKEN:
            print("Error: DISCORD_BOT_TOKEN not set in .env file")
            return
        
        # Start bot in daemon thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Wait for bot to connect (up to 30 seconds)
        print("Waiting for bot to connect...")
        max_wait = 30
        for i in range(max_wait * 2):  # Check every 0.5 seconds
            await asyncio.sleep(0.5)
            bot = get_bot_instance()
            if bot and bot.is_ready():
                print(f"✓ Bot connected as {bot.user}")
                break
        else:
            print("Error: Bot failed to connect within 30 seconds")
            return
    
    # Fetch real messages from Discord
    print("\n[2/4] Fetching real Discord messages...")
    try:
        messages = await scrape_discord_history()
        print(f"✓ Fetched {len(messages)} messages from Discord")
        
        if not messages:
            print("Warning: No messages found. Make sure there are messages in Discord channels.")
            return
        
        # Show first few messages
        print("\nSample messages:")
        for i, msg in enumerate(messages[:5], 1):
            print(f"  {i}. [{msg.username}]: {msg.content[:100]}...")
        if len(messages) > 5:
            print(f"  ... and {len(messages) - 5} more messages")
    
    except Exception as e:
        print(f"Error fetching messages: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Clear existing questions for clean test
    initial_question_count = len(questions)
    print(f"\n[3/4] Starting with {initial_question_count} existing questions")
    
    # Test the extraction and assignment
    print("\n[4/4] Extracting questions and assigning messages...")
    try:
        question_ids = await assign_messages_to_existing_questions(messages)
        print(f"✓ Extracted {len(question_ids)} questions")
        
        # Display results
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        print(f"Total questions after extraction: {len(question_ids)}")
        print(f"New questions created: {len(question_ids) - initial_question_count}")
        
        print("\nQuestions and their message counts:")
        for qid in question_ids:
            qstate = questions.get(qid)
            if qstate:
                print(f"\n  Question ID: {qid}")
                print(f"  Question Text: {qstate.question}")
                print(f"  Messages assigned: {len(qstate.discord_messages)}")
                print(f"  Sample messages:")
                for msg in qstate.discord_messages[:3]:
                    print(f"    - [{msg.username}]: {msg.content[:80]}...")
                if len(qstate.discord_messages) > 3:
                    print(f"    ... and {len(qstate.discord_messages) - 3} more")
        
        print("\n" + "=" * 80)
        print("✓ Test completed successfully!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_extract_and_assign_messages())

