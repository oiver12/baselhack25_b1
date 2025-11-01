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



async def generate_two_word_summary(
    messages: List[str], 
    existing_groups: Optional[List[dict]] = None,
    question_id: Optional[str] = None
) -> List[str]:
    """
    Cluster messages into as few groups as possible and generate 2-word summaries.
    Reuses existing groups when messages fit, only creates new labels when needed.
    
    Args:
        messages: List of message texts
        existing_groups: Optional list of existing groups, each with 'title' and 'sample_messages'
        question_id: Optional question ID to fetch existing groups from state
        
    Returns:
        List of 2-word summaries (one per cluster)
    """
    if not messages:
        return []
    
    # Fetch existing groups from state if question_id is provided
    if question_id and not existing_groups:
        question_state = get_question_state(question_id)
        if question_state and question_state.suggestions:
            existing_groups = []
            for suggestion in question_state.suggestions:
                # Get sample messages from people_opinions
                sample_messages = [opinion.message for opinion in suggestion.people_opinions]
                existing_groups.append({
                    'title': suggestion.title,
                    'sample_messages': sample_messages
                })
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    if len(messages) == 1:
        # Single message, check if it fits existing groups first
        if existing_groups:
            single_msg_embedding = client.embeddings.create(
                input=[messages[0]],
                model="text-embedding-3-small",
            )
            single_emb = np.array([single_msg_embedding.data[0].embedding])
            
            for group in existing_groups:
                if group['sample_messages']:
                    group_embeddings = client.embeddings.create(
                        input=group['sample_messages'][:3],  # Use first 3 as samples
                        model="text-embedding-3-small",
                    )
                    group_embs = np.array([item.embedding for item in group_embeddings.data])
                    similarities = cosine_similarity(single_emb, group_embs)
                    max_similarity = np.max(similarities)
                    
                    if max_similarity >= 0.7:  # Threshold for matching
                        return [group['title']]  # Reuse existing label
        
        # No match found, create new summary
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
        words = summary.split()[:2]
        return [" ".join(words)]
    
    # Generate embeddings for all messages
    embedding_response = client.embeddings.create(
        input=messages,
        model="text-embedding-3-small",
    )
    
    embeddings = np.array([item.embedding for item in embedding_response.data])
    
    # Match messages to existing groups first
    matched_to_existing = {}  # message_idx -> group_title
    unmatched_indices = set(range(len(messages)))
    
    if existing_groups:
        # For each existing group, get representative embeddings
        for group in existing_groups:
            if not group['sample_messages']:
                continue
                
            # Get embeddings for sample messages from existing group
            sample_embeddings_response = client.embeddings.create(
                input=group['sample_messages'][:5],  # Use first 5 as representative samples
                model="text-embedding-3-small",
            )
            group_embeddings = np.array([item.embedding for item in sample_embeddings_response.data])
            
            # Calculate similarity between new messages and this group
            similarities = cosine_similarity(embeddings, group_embeddings)
            max_similarities = np.max(similarities, axis=1)  # Max similarity per message
            
            # Match messages with similarity >= 0.7 to this group
            for msg_idx in list(unmatched_indices):
                if max_similarities[msg_idx] >= 0.7:
                    matched_to_existing[msg_idx] = group['title']
                    unmatched_indices.remove(msg_idx)
    
    # Collect all unique existing labels that were matched
    existing_labels_used = set(matched_to_existing.values()) if matched_to_existing else set()
    summaries = list(existing_labels_used)  # Start with existing labels
    
    # Now cluster only the unmatched messages (if any)
    if unmatched_indices:
        unmatched_list = list(unmatched_indices)
        unmatched_messages = [messages[i] for i in unmatched_list]
        unmatched_embeddings = embeddings[unmatched_list]
        
        if len(unmatched_messages) == 1:
            # Single unmatched message - just summarize it
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise 2-word summaries. Respond with exactly 2 words separated by a space. No punctuation."},
                    {"role": "user", "content": f"Summarize this message in exactly 2 words:\n{unmatched_messages[0]}"}
                ],
                max_tokens=10,
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            words = summary.split()[:2]
            summaries.append(" ".join(words))
        else:
            # Multiple unmatched messages - cluster them
            # Calculate cosine similarity matrix for unmatched messages
            unmatched_similarity_matrix = cosine_similarity(unmatched_embeddings)
            unmatched_distance_matrix = 1 - unmatched_similarity_matrix
            
            # Use hierarchical clustering
            best_unmatched_clusters = None
            min_clusters = 1
            max_clusters = len(unmatched_messages)
            
            # Binary search for minimum clusters
            while min_clusters < max_clusters:
                n_clusters = (min_clusters + max_clusters) // 2
                
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    metric='precomputed',
                    linkage='average'
                )
                cluster_labels = clustering.fit_predict(unmatched_distance_matrix)
                
                # Check if clusters are meaningful
                valid = True
                for cluster_id in range(n_clusters):
                    cluster_indices = np.where(cluster_labels == cluster_id)[0]
                    if len(cluster_indices) > 1:
                        cluster_similarities = unmatched_similarity_matrix[np.ix_(cluster_indices, cluster_indices)]
                        avg_similarity = np.mean(cluster_similarities[np.triu_indices_from(cluster_similarities, k=1)])
                        if avg_similarity < 0.5:
                            valid = False
                            break
                
                if valid:
                    best_unmatched_clusters = cluster_labels
                    max_clusters = n_clusters
                else:
                    min_clusters = n_clusters + 1
            
            # If no good clustering found, use default
            if best_unmatched_clusters is None:
                clustering = AgglomerativeClustering(
                    n_clusters=min(5, len(unmatched_messages)),
                    metric='precomputed',
                    linkage='average'
                )
                best_unmatched_clusters = clustering.fit_predict(unmatched_distance_matrix)
            
            # Group unmatched messages by cluster
            unique_unmatched_clusters = np.unique(best_unmatched_clusters)
            unmatched_cluster_groups = {cluster_id: [] for cluster_id in unique_unmatched_clusters}
            
            for idx, cluster_id in enumerate(best_unmatched_clusters):
                unmatched_cluster_groups[cluster_id].append(unmatched_messages[idx])
            
            # Generate 2-word summary for each new cluster
            for cluster_id in unique_unmatched_clusters:
                cluster_messages = unmatched_cluster_groups[cluster_id]
                
                # Combine messages in cluster for summarization
                combined_text = "\n".join(cluster_messages[:5])
                if len(cluster_messages) > 5:
                    combined_text += f"\n... and {len(cluster_messages) - 5} more similar messages"
                
                # Tell AI to use existing groups as reference
                existing_context = ""
                if existing_groups:
                    existing_titles = [g['title'] for g in existing_groups]
                    existing_context = f"\n\nNote: There are already these existing groups: {', '.join(existing_titles)}. Only create a new label if this message doesn't fit into any of them."
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise 2-word summaries. Respond with exactly 2 words separated by a space. No punctuation."},
                        {"role": "user", "content": f"Summarize these messages in exactly 2 words:\n{combined_text}{existing_context}"}
                    ],
                    max_tokens=10,
                    temperature=0.3
                )
                
                summary = response.choices[0].message.content.strip()
                words = summary.split()[:2]
                new_summary = " ".join(words)
                summaries.append(new_summary)
    
    # If all messages matched to existing groups, just return those labels
    # (summaries already contains existing_labels_used, so this is handled above)
    
    return sorted(set(summaries))  # Return unique summaries, sorted for consistency

    

async def classify_message(message: [str]) -> [str]:
    """
    Classify messages as good, neutral or bad 
    
    Args:
        messages: Messages text
        
    Returns:
        Classification: "good", "neutral" or "bad"
    """
    # TODO: Implement message classification
    # - Analyze message complexity
    # - Check length, vocabulary, structure
    # - Classify based on criteria
    # Use OpenAI to classify each message as 'good', 'neutral' or 'bad'
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    results = []
    for msg in message:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Classify the following message as 'good', 'neutral' or 'bad'. Respond with ONLY 'good', 'neutral' or 'bad'."},
                {"role": "user", "content": f"Classify this message: {msg}"}
            ],
            max_tokens=2,
            temperature=0.0,
        )
        label = response.choices[0].message.content.strip().lower()
        if label not in {"good", "neutral", "bad"}:
            label = "neutral"
        results.append(label)
    return results

async def find_excellent_message(messages: [str], class_labels: [str]) -> str:
    """
    Find the excellent message in a list of messages
    
    Args:
        messages: Messages text
        class_labels: Class labels
        
    Returns:
        Excellent message
    """
    # INSERT_YOUR_CODE
    # Filter out messages with class label 'bad'
    filtered_messages = [msg for msg, label in zip(messages, class_labels) if label == "good"]
    if not filtered_messages:
        return None  # or you might want to return a default/fallback value
    # INSERT_YOUR_CODE
    # If only one good message, return it
    if len(filtered_messages) == 1:
        return filtered_messages[0]
    # Use OpenAI to select the "most excellent" from filtered good messages
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = (
        "Given the following messages, select the single one that best exemplifies clarity, helpfulness, and quality. "
        "Return only the exact message text (no explanation, no extra text):\n\n"
    )
    for idx, msg in enumerate(filtered_messages):
        prompt += f"{idx+1}. {msg}\n"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a wise evaluator of messages."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.0,
    )
    result_message = response.choices[0].message.content.strip()
    # If result is not in filtered_messages, fall back to first good
    if result_message in filtered_messages:
        return result_message
    else:
        # Sometimes LLM might return a snippet, attempt fuzzy match
        for msg in filtered_messages:
            if result_message in msg or msg in result_message:
                return msg
        return filtered_messages[0]
    

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

