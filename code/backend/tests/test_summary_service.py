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
from app.services.summary_service import (
    generate_two_word_summary,
    classify_message,
    find_excellent_message
)
from app.state import create_question_state, get_question_state
from openai import OpenAI
from app.config import settings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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
    "lionels cock is too small",
    "Lionel has a very big cock",
    "I want to suck lionels big hairy cock"


]


async def test_generate_two_word_summary():
    """Test the clustering function with dummy data"""
    # Use inline data first (updated), fallback to JSON file
    messages = DUMMY_MESSAGES or load_dummy_messages()
    
    # Create a test question state to enable caching (or get existing one)
    test_question_id = "test-question-123"
    existing_state = get_question_state(test_question_id)
    if not existing_state:
        create_question_state(test_question_id, "Test question for caching")
        print("📝 Created new question state for caching")
    else:
        cached_count = len(existing_state.message_classifications)
        print(f"📦 Using existing state with {cached_count} cached classifications")
    
    print(f"Testing with {len(messages)} messages:")
    print("-" * 80)
    for i, msg in enumerate(messages, 1):
        print(f"{i}. {msg}")
    print("-" * 80)
    print("\nRunning clustering...\n")
    
    try:
        # Get cluster summaries
        cluster_summaries = await generate_two_word_summary(messages)
        
        # Classify all messages once (with caching enabled via question_id)
        print("\nClassifying messages (using cache if available)...")
        state_before = get_question_state(test_question_id)
        cached_before = len(state_before.message_classifications) if state_before else 0
        
        classifications = await classify_message(messages, question_id=test_question_id)
        
        state_after = get_question_state(test_question_id)
        cached_after = len(state_after.message_classifications) if state_after else 0
        newly_cached = cached_after - cached_before
        print(f"   ✓ Cached {cached_after} total classifications ({newly_cached} new, {cached_before} from cache)")
        
        # Find excellent message once (with caching enabled via question_id)
        print("Finding excellent message (using cache if available)...")
        state_before_excellent = get_question_state(test_question_id)
        had_excellent_cache = state_before_excellent.excellent_message if state_before_excellent else None
        
        excellent_message = await find_excellent_message(messages, classifications, question_id=test_question_id)
        
        if had_excellent_cache:
            print(f"   ✓ Used cached excellent message")
        else:
            print(f"   ✓ Found and cached excellent message")
        
        # Determine which cluster each message belongs to
        # Get embeddings for all messages and cluster summaries
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Get embeddings for messages
        msg_embeddings_resp = client.embeddings.create(
            input=messages,
            model="text-embedding-3-small",
        )
        msg_embeddings = np.array([item.embedding for item in msg_embeddings_resp.data])
        
        # Get embeddings for cluster summaries
        cluster_embeddings_resp = client.embeddings.create(
            input=cluster_summaries,
            model="text-embedding-3-small",
        )
        cluster_embeddings = np.array([item.embedding for item in cluster_embeddings_resp.data])
        
        # Calculate similarity and assign messages to clusters
        similarities = cosine_similarity(msg_embeddings, cluster_embeddings)
        message_clusters = np.argmax(similarities, axis=1)  # Index of best matching cluster
        
        print("\n" + "=" * 80)
        print("CLUSTERING RESULTS:")
        print("=" * 80)
        print(f"\n✓ Clustered into {len(cluster_summaries)} distinct groups:")
        for i, summary in enumerate(cluster_summaries):
            print(f"  Cluster {i+1}: {summary}")
        
        print("\n" + "-" * 80)
        print("MESSAGE DETAILS:")
        print("-" * 80)
        for i, (msg, cluster_idx, classification) in enumerate(zip(messages, message_clusters, classifications), 1):
            cluster_name = cluster_summaries[cluster_idx]
            is_excellent = "⭐ EXCELLENT" if excellent_message and msg == excellent_message else ""
            
            print(f"\n[{i}] {msg}")
            print(f"     Cluster: {cluster_name} (Cluster {cluster_idx + 1})")
            print(f"     Classification: {classification.upper()}")
            if is_excellent:
                print(f"     Status: {is_excellent}")
        
        if excellent_message:
            print(f"\n⭐ Excellent Message Found: {excellent_message}")
        else:
            print(f"\n⚠ No excellent message found (no 'good' messages or selection failed)")
        
        print("\n" + "=" * 80)
        print(f"✓ Summary: {len(messages)} messages → {len(cluster_summaries)} clusters")
        print("=" * 80)
        
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

