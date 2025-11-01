"""
Service for generating summaries and classifications
"""
from typing import Optional, List
from app.state import get_question_state
from app.config import settings
from openai import OpenAI
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity



async def generate_two_word_summary(messages: List[str]) -> List[str]:
    """
    Cluster messages into as few groups as possible and generate 2-word summaries
    
    Args:
        messages: List of message texts
        
    Returns:
        List of 2-word summaries (one per cluster)
    """
    if not messages:
        return []
    
    if len(messages) == 1:
        # Single message, just summarize it
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise 2-word summaries. Respond with exactly 2 words separated by a space."},
                {"role": "user", "content": f"Summarize this message in exactly 2 words: {messages[0]}"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        return [summary]
    
    # Generate embeddings for all messages
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    embedding_response = client.embeddings.create(
        input=messages,
        model="text-embedding-3-small",
    )
    
    embeddings = np.array([item.embedding for item in embedding_response.data])
    
    # Calculate cosine similarity matrix
    similarity_matrix = cosine_similarity(embeddings)
    
    # Use hierarchical clustering to minimize clusters
    # Convert similarity to distance (1 - similarity)
    distance_matrix = 1 - similarity_matrix
    
    # Start with max clusters and reduce until we find optimal grouping
    # Use a threshold approach: merge clusters with similarity > threshold
    best_clusters = None
    min_clusters = 1
    max_clusters = len(messages)
    
    # Try different numbers of clusters, preferring fewer
    # We'll use a similarity threshold approach
    threshold = 0.7  # Start with high similarity requirement
    
    # Binary search for minimum clusters that still makes sense
    while min_clusters < max_clusters:
        n_clusters = (min_clusters + max_clusters) // 2
        
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='precomputed',
            linkage='average'
        )
        cluster_labels = clustering.fit_predict(distance_matrix)
        
        # Check if clusters are meaningful (average intra-cluster similarity)
        valid = True
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            if len(cluster_indices) > 1:
                cluster_similarities = similarity_matrix[np.ix_(cluster_indices, cluster_indices)]
                avg_similarity = np.mean(cluster_similarities[np.triu_indices_from(cluster_similarities, k=1)])
                if avg_similarity < 0.5:  # Threshold for meaningful clusters
                    valid = False
                    break
        
        if valid:
            best_clusters = cluster_labels
            max_clusters = n_clusters
        else:
            min_clusters = n_clusters + 1
    
    # If no good clustering found, use default
    if best_clusters is None:
        clustering = AgglomerativeClustering(
            n_clusters=min(5, len(messages)),
            metric='precomputed',
            linkage='average'
        )
        best_clusters = clustering.fit_predict(distance_matrix)
    
    # Group messages by cluster
    unique_clusters = np.unique(best_clusters)
    cluster_groups = {cluster_id: [] for cluster_id in unique_clusters}
    
    for idx, cluster_id in enumerate(best_clusters):
        cluster_groups[cluster_id].append(messages[idx])
    
    # Generate 2-word summary for each cluster
    summaries = []
    for cluster_id in unique_clusters:
        cluster_messages = cluster_groups[cluster_id]
        
        # Combine messages in cluster for summarization
        combined_text = "\n".join(cluster_messages[:5])  # Limit to first 5 messages for context
        if len(cluster_messages) > 5:
            combined_text += f"\n... and {len(cluster_messages) - 5} more similar messages"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise 2-word summaries. Respond with exactly 2 words separated by a space. No punctuation."},
                {"role": "user", "content": f"Summarize these messages in exactly 2 words:\n{combined_text}"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        # Clean up the summary to ensure it's exactly 2 words
        words = summary.split()[:2]
        summary = " ".join(words)
        summaries.append(summary)
    
    return summaries

    

async def classify_message(message: str) -> str:
    """
    Classify a message as sophisticated or neutral
    
    Args:
        message: Message text
        
    Returns:
        Classification: "sophisticated" or "neutral"
    """
    # TODO: Implement message classification
    # - Analyze message complexity
    # - Check length, vocabulary, structure
    # - Classify based on criteria
    
    return "neutral"


async def summarize_followup_messages(user_id: str, question_id: str) -> Optional[str]:
    """
    Summarize all followup messages from a user for a question
    
    Args:
        user_id: Discord user ID
        question_id: Question ID
        
    Returns:
        Summary of all messages, or None if no followup messages
    """
    # TODO: Implement followup message summarization
    # - Get all messages from user for this question
    # - If multiple messages, summarize them
    # - Return summary or None if single message
    
    question_state = get_question_state(question_id)
    if not question_state:
        return None
    
    user_messages = [
        msg for msg in question_state.discord_messages
        if msg.user_id == user_id
    ]
    
    if len(user_messages) <= 1:
        return None
    
    # TODO: Generate summary of multiple messages
    return "Summarized messages from user"

