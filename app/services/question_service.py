"""
Message relevance checking and historical message analysis for active question
"""
from typing import List
from app.state import DiscordMessage, get_active_question, global_historical_messages, QuestionState
from app.config import settings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


async def check_message_relevance(message: DiscordMessage, question_text: str) -> bool:
    """
    Check if a message is relevant to a question using embedding similarity.
    
    Args:
        message: The Discord message to check
        question_text: The question text to compare against
        
    Returns:
        True if message is relevant (similarity >= 0.5), False otherwise
    """
    from app.services.embedding_cache import get_embeddings_batch
    
    # Get embeddings for message and question text
    texts = [message.content, question_text]
    embeddings = await get_embeddings_batch(texts, use_cache=True)
    
    message_embedding = embeddings[0:1]  # First embedding (message)
    question_embedding = embeddings[1:2]  # Second embedding (question)
    
    # Compute cosine similarity
    similarity = cosine_similarity(message_embedding, question_embedding)[0][0]
    
    threshold = 0.3
    print(f"Similarity: {similarity}, Threshold: {threshold}")
    print(f"Message: {message.content}, Question: {question_text}")
    return similarity >= threshold


async def analyze_historical_messages_for_question(question: QuestionState) -> None:
    """
    Analyze all historical cached messages and add relevant ones to the question.
    Skips messages already in the question.
    
    Args:
        question: The active question state to analyze messages for
    """
    if not question:
        return
    
    # Get all historical messages, excluding those already in the question
    existing_message_ids = {msg.message_id for msg in question.discord_messages}
    candidate_messages = [
        msg for msg in global_historical_messages
        if msg.message_id not in existing_message_ids
    ]
    
    if not candidate_messages:
        print(f"No new historical messages to analyze for question: {question.question}")
        return
    
    print(f"Analyzing {len(candidate_messages)} historical messages for relevance to question: {question.question}")
    
    # Check relevance for each message
    from app.state import should_ignore_message_for_cache
    
    relevant_messages = []
    for msg in candidate_messages:
        # Skip meta-messages like !start_discussion commands
        if should_ignore_message_for_cache(msg.content):
            continue
        is_relevant = await check_message_relevance(msg, question.question)
        if is_relevant:
            # Set question_id on message
            msg.question_id = question.question_id
            relevant_messages.append(msg)
    
    print(f"Found {len(relevant_messages)} relevant messages out of {len(candidate_messages)}")
    
    # Add relevant messages to question
    for msg in relevant_messages:
        # Check again if message already exists (avoid duplicates)
        if not any(m.message_id == msg.message_id for m in question.discord_messages):
            question.discord_messages.append(msg)
            
            # Update participants
            if msg.user_id not in question.participants:
                from app.state import Participant
                question.participants[msg.user_id] = Participant(
                    user_id=msg.user_id,
                    username=msg.username,
                    profile_pic_url=msg.profile_pic_url,
                )
            question.participants[msg.user_id].message_count += 1
    
    # Save state after adding messages
    if relevant_messages:
        from app.state import save_all_questions
        save_all_questions()
        print(f"Added {len(relevant_messages)} relevant historical messages to question")
