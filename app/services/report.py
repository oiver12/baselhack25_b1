"""
Report service for vector analysis and dimension reduction of question answers
"""
from typing import List, Dict, Any
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from app.state import QuestionState, DiscordMessage
from app.services.embedding_cache import get_embeddings_batch
from app.services.llm_service import generate_bullet_point_summary_with_pros_cons

async def make_2d_plot(question_state: QuestionState) -> List[Dict[str, Any]]:
    """
    Perform vector analysis on all answers in a QuestionState and reduce to 2D coordinates.
    
    Args:
        question_state: The QuestionState containing messages to analyze
        
    Returns:
        List of dictionaries, each containing:
        - message_id: str
        - x: float (between -1 and 1)
        - y: float (between -1 and 1)
        - message: DiscordMessage object
    """
    if not question_state.discord_messages:
        return []
    
    # Extract message contents for embedding
    message_texts = [msg.content for msg in question_state.discord_messages]
    
    # Get embeddings directly from API without using cache
    embeddings = await get_embeddings_batch(message_texts, use_cache=False)
    
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
            "message": msg.content,  # Include full message object for reference
            "name": msg.username,
            "profile_pic_url": msg.profile_pic_url,
            "two_word_summary": msg.two_word_summary,
            "classification": msg.classification,
            "is_excellent": msg.is_excellent,
        })
    
    return results
    
async def get_whole_Report(question_state: QuestionState) -> Dict[str, Any]:
    """
    Get the whole report for a question
    """
    results = await make_2d_plot(question_state)
    summary = await generate_bullet_point_summary_with_pros_cons([msg.content for msg in question_state.discord_messages])
    
    # Try to parse JSON, otherwise keep as string
    try:
        summary_dict = json.loads(summary)
    except json.JSONDecodeError:
        # If not valid JSON, keep as string
        summary_dict = summary
    
    return {
        "results": results,
        "question": "What is the risk of using ai in business?",
        "summary": summary_dict
    }
