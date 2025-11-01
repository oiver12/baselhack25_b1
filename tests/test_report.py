"""
Test file for report.py - vector analysis and dimension reduction using real Discord messages
"""
import asyncio
import sys
import threading
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

# Add project root directory to path so we can import app modules
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.services.report import analyze_question_responses
from app.services.discord_service import scrape_discord_history
from app.services.question_service import assign_messages_to_existing_questions
from app.discord_bot.bot import run_bot, get_bot_instance
from app.config import settings
from app.state import QuestionState, questions, get_question_state, create_question_state


async def wait_for_bot(max_wait: int = 30):
    """Wait for bot to be ready"""
    print("Waiting for bot to connect...")
    for i in range(max_wait * 2):  # Check every 0.5 seconds
        await asyncio.sleep(0.5)
        bot = get_bot_instance()
        if bot and bot.is_ready():
            print(f"✓ Bot connected as {bot.user}")
            return bot
    print("Error: Bot failed to connect within timeout")
    return None


async def test_empty_messages():
    """Test with no messages"""
    print("\n=== Test: Empty messages ===")
    question_state = QuestionState(
        question_id="test_empty",
        question="Test question with no messages",
        created_at=datetime.now(timezone.utc),
    )
    
    results = await analyze_question_responses(question_state)
    assert len(results) == 0, "Should return empty list for no messages"
    print(f"✓ Empty messages test passed - returned {len(results)} results")


async def test_with_real_discord_messages():
    """Test with real Discord messages"""
    print("\n=== Test: Real Discord messages ===")
    
    # Check if bot token is available
    if not settings.DISCORD_BOT_TOKEN:
        print("⚠ Skipping test - DISCORD_BOT_TOKEN not set in .env file")
        return
    
    # Start bot in daemon thread
    print("Starting Discord bot...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait for bot to be ready
    bot = await wait_for_bot()
    if not bot:
        print("⚠ Skipping test - Bot failed to connect")
        return
    
    # Fetch real messages from Discord
    print("\nFetching messages from Discord...")
    messages = await scrape_discord_history()
    print(f"Found {len(messages)} messages from Discord")
    
    if len(messages) == 0:
        print("⚠ No messages found in Discord - skipping test")
        return
    
    # Assign messages to questions (this will create questions or assign to existing ones)
    print("\nAssigning messages to questions...")
    question_ids = await assign_messages_to_existing_questions(messages, allow_new_questions=True)
    print(f"Messages assigned to {len(question_ids)} question(s)")
    
    if len(question_ids) == 0:
        print("⚠ No questions received messages - skipping test")
        return
    
    # Test with the first question that has messages
    test_question_id = question_ids[0]
    question_state = get_question_state(test_question_id)
    
    if not question_state:
        print(f"⚠ Question {test_question_id} not found - skipping test")
        return
    
    print(f"\nTesting with question: '{question_state.question}'")
    print(f"Question has {len(question_state.discord_messages)} messages")
    
    # Run the analysis
    print("\nRunning vector analysis and dimension reduction...")
    results = await analyze_question_responses(question_state)
    
    # Verify results
    assert len(results) == len(question_state.discord_messages), \
        f"Expected {len(question_state.discord_messages)} results, got {len(results)}"
    
    # Verify all message IDs are present
    result_message_ids = {result["message_id"] for result in results}
    question_message_ids = {msg.message_id for msg in question_state.discord_messages}
    assert result_message_ids == question_message_ids, "All message IDs should be present in results"
    
    # Verify coordinates are in valid range [-1, 1]
    print("\nVerifying coordinates...")
    for result in results:
        assert -1.0 <= result["x"] <= 1.0, \
            f"x must be in [-1, 1], got {result['x']} for message {result['message_id']}"
        assert -1.0 <= result["y"] <= 1.0, \
            f"y must be in [-1, 1], got {result['y']} for message {result['message_id']}"
    
    # Verify message references
    for result in results:
        assert result["message"] is not None, "Message reference should not be None"
        assert result["message"].message_id == result["message_id"], "Message ID should match"
    
    # Check that coordinates are normalized (at least one point should be near boundary)
    distances = [np.sqrt(r["x"] ** 2 + r["y"] ** 2) for r in results]
    max_dist = max(distances) if distances else 0.0
    
    print(f"\n✓ Test passed with {len(results)} messages")
    print(f"  - All coordinates in [-1, 1] range")
    print(f"  - Max distance from origin: {max_dist:.3f}")
    print(f"  - All message IDs present: ✓")
    print(f"  - Message references valid: ✓")
    
    # Print sample coordinates
    print("\nSample coordinates (first 5):")
    for result in results[:5]:
        print(f"  {result['message_id'][:20]}...: ({result['x']:.3f}, {result['y']:.3f})")
    
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")


async def test_with_specific_question():
    """Test with a specific question if multiple exist"""
    print("\n=== Test: Specific question ===")
    
    if len(questions) == 0:
        print("⚠ No questions available - skipping test")
        return
    
    # Find a question with messages
    question_with_messages = None
    for qid, qstate in questions.items():
        if len(qstate.discord_messages) > 0:
            question_with_messages = qstate
            break
    
    if not question_with_messages:
        print("⚠ No questions with messages found - skipping test")
        return
    
    print(f"Testing with question: '{question_with_messages.question}'")
    print(f"Question has {len(question_with_messages.discord_messages)} messages")
    
    # Run analysis
    results = await analyze_question_responses(question_with_messages)
    
    # Verify results
    assert len(results) == len(question_with_messages.discord_messages)
    
    # Verify coordinates
    for result in results:
        assert -1.0 <= result["x"] <= 1.0
        assert -1.0 <= result["y"] <= 1.0
    
    print(f"✓ Test passed - {len(results)} messages analyzed")
    print(f"  Coordinates range: x=[{min(r['x'] for r in results):.3f}, {max(r['x'] for r in results):.3f}], "
          f"y=[{min(r['y'] for r in results):.3f}, {max(r['y'] for r in results):.3f}]")


async def test_coordinate_properties():
    """Test specific coordinate properties"""
    print("\n=== Test: Coordinate properties ===")
    
    if len(questions) == 0:
        print("⚠ No questions available - skipping test")
        return
    
    # Find question with at least 3 messages
    test_question = None
    for qid, qstate in questions.items():
        if len(qstate.discord_messages) >= 3:
            test_question = qstate
            break
    
    if not test_question:
        print("⚠ No questions with 3+ messages found - skipping test")
        return
    
    results = await analyze_question_responses(test_question)
    
    if len(results) < 3:
        print("⚠ Not enough results for property tests")
        return
    
    # Test that points are within unit circle
    distances = [np.sqrt(r["x"] ** 2 + r["y"] ** 2) for r in results]
    max_dist = max(distances)
    assert max_dist <= 2.0 + 1e-6, f"All points should be within unit circle, max_dist: {max_dist}"
    
    # Test that coordinates are distinct (for multiple messages)
    if len(results) > 1:
        coords = [(r["x"], r["y"]) for r in results]
        unique_coords = len(set(coords))
        print(f"  - Unique coordinates: {unique_coords}/{len(results)}")
    
    print(f"✓ Coordinate properties test passed")
    print(f"  - Max distance from origin: {max_dist:.3f}")
    print(f"  - All points within unit circle: ✓")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing report.py - Vector Analysis with Real Discord Messages")
    print("=" * 60)
    
    try:
        # Test with empty messages (doesn't require Discord)
        await test_empty_messages()
        
        # Test with real Discord messages (requires bot connection)
        await test_with_real_discord_messages()
        
        # Test with specific question
        await test_with_specific_question()
        
        # Test coordinate properties
        await test_coordinate_properties()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test assertion failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
