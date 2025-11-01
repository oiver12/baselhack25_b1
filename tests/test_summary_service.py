"""
Test file for summary_service
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root directory to path so we can import app modules
# Get the absolute path to the project root (parent of tests/)
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Now we can import from app
from app.services.summary_service import generate_two_word_summary

# Load dummy data from fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DUMMY_MESSAGES_FILE = FIXTURES_DIR / "dummy_messages.json"

def load_dummy_messages():
    """Load dummy messages from JSON file"""
    if DUMMY_MESSAGES_FILE.exists():
        with open(DUMMY_MESSAGES_FILE, 'r') as f:
            data = json.load(f)
            return data.get("messages", [])
    return []


# Inline dummy data as fallback
DUMMY_MESSAGES = [
    "I think the email service is working very well",
    "Marketing needs more funding to succeed",
    "Let's allocate more money to marketing campaigns",
    "The team already as very good communication tools",
    "We should improve how teams communicate",
    "Communication between departments is lacking",
    "Maybe we could use Slack or Discord",
    "We need a better chat platform for collaboration",
    "The current email system is too slow",
    "Email communication is outdated and inefficient",
    "Our workflow would benefit from instant messaging",
    "I propose we adopt a new project management tool",
    "We should implement better project tracking software",
    "Let's use Jira or Asana for task management",
    "lionles cock is too small"

]


async def test_generate_two_word_summary():
    """Test the clustering function with dummy data"""
    # Use inline data first (updated), fallback to JSON file
    messages = DUMMY_MESSAGES or load_dummy_messages()
    
    print(f"Testing with {len(messages)} messages:")
    print("-" * 60)
    for i, msg in enumerate(messages, 1):
        print(f"{i}. {msg}")
    print("-" * 60)
    print("\nRunning clustering...\n")
    
    try:
        result = await generate_two_word_summary(messages)
        
        print(f"✓ Clustered into {len(result)} distinct groups:")
        print("=" * 60)
        for i, summary in enumerate(result, 1):
            print(f"{i}. {summary}")
        print("=" * 60)
        print(f"\n✓ Reduced {len(messages)} messages to {len(result)} 2-word summaries")
        print(result)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_empty_messages():
    """Test with empty input"""
    print("\n--- Testing empty messages ---")
    result = await generate_two_word_summary([])
    assert result == [], "Empty list should return empty list"
    print("✓ Empty messages handled correctly")


async def test_single_message():
    """Test with single message"""
    print("\n--- Testing single message ---")
    result = await generate_two_word_summary(["We need better tools"])
    assert len(result) == 1, "Single message should return one summary"
    assert len(result[0].split()) == 2, "Summary should be exactly 2 words"
    print(f"✓ Single message: {result[0]}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing generate_two_word_summary function")
    print("=" * 60)
    
    # Run main test
    asyncio.run(test_generate_two_word_summary())
    
    # Run edge case tests
    asyncio.run(test_empty_messages())
    asyncio.run(test_single_message())

