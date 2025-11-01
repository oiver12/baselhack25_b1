"""
Report service for vector analysis and dimension reduction of question answers
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from app.state import QuestionState, DiscordMessage
from app.services.embedding_cache import get_cached_embedding, get_embeddings_batch


async def analyze_question_responses(question_state: QuestionState) -> List[Dict[str, Any]]:
    """
    Perform vector analysis on all answers in a QuestionState and reduce to 2D coordinates.
    
    Args:
        question_state: The QuestionState containing messages to analyze
        
    Returns:
        List of dictionaries, each containing:
        - message_id: str
        - x: float (between -1 and 1)
        - y: float (between -1 and 1)
        - message: DiscordMessage object (or reference)
    """
    if not question_state.discord_messages:
        return []
    
    # Extract message contents for embedding
    message_texts = [msg.content for msg in question_state.discord_messages]
    
    # Get embeddings from cache first, then fetch missing ones
    cached_embeddings = []
    uncached_indices = []
    uncached_messages = []
    
    for i, msg_text in enumerate(message_texts):
        cached = get_cached_embedding(msg_text)
        if cached is not None:
            cached_embeddings.append((i, cached))
        else:
            uncached_indices.append(i)
            uncached_messages.append(msg_text)
    
    # Fetch embeddings for messages not in cache
    embeddings_list = [None] * len(message_texts)
    
    # Fill in cached embeddings
    for idx, emb in cached_embeddings:
        embeddings_list[idx] = emb
    
    # Fetch uncached embeddings if any
    if uncached_messages:
        uncached_embeddings = await get_embeddings_batch(uncached_messages, use_cache=True)
        for i, uncached_idx in enumerate(uncached_indices):
            embeddings_list[uncached_idx] = uncached_embeddings[i]
    
    # Convert to numpy array
    embeddings = np.array(embeddings_list)
    
    # Perform dimension reduction to 2D
    # Using PCA for deterministic results (t-SNE is stochastic and slower)
    if len(message_texts) == 1:
        # Single message: place at origin
        coords_2d = np.array([[0.0, 0.0]])
    elif len(message_texts) == 2:
        # Two messages: place them at opposite ends
        coords_2d = np.array([[-0.5, 0.0], [0.5, 0.0]])
    else:
        # Multiple messages: use PCA for dimension reduction
        pca = PCA(n_components=2)
        coords_2d = pca.fit_transform(embeddings)
        
        # Alternative: Use t-SNE for non-linear dimension reduction (uncomment if preferred)
        # tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(message_texts) - 1))
        # coords_2d = tsne.fit_transform(embeddings)
    
    # Normalize coordinates to be between -1 and 1
    if coords_2d.shape[0] > 1:
        # Find the maximum absolute value across both dimensions
        max_abs = np.max(np.abs(coords_2d))
        if max_abs > 0:
            # Normalize so the furthest point is at distance 1 from origin
            coords_2d = coords_2d / max_abs
        # Clamp to ensure all points are within [-1, 1] range
        coords_2d = np.clip(coords_2d, -1.0, 1.0)
    
    # Build result list with message metadata
    results = []
    for i, msg in enumerate(question_state.discord_messages):
        results.append({
            "message_id": msg.message_id,
            "x": float(coords_2d[i][0]),
            "y": float(coords_2d[i][1]),
            "message": msg,  # Include full message object for reference
        })
    
    return results

