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
    
    # Get embeddings directly from API
    embeddings = await get_embeddings_batch(message_texts, use_cache=True)
    
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
    from app.services.noble_message_service import compute_noble_messages_for_clusters
    
    import asyncio
    results_task = asyncio.create_task(make_2d_plot(question_state))
    summary_task = asyncio.create_task(generate_bullet_point_summary_with_pros_cons(
        [msg.content for msg in question_state.discord_messages],
        question=question_state.question
    ))
    
    # Compute noble messages for all clusters
    await compute_noble_messages_for_clusters(question_state)
    
    results, summary = await asyncio.gather(results_task, summary_task)
    
    # Build noble messages map per cluster with expert information
    from app.services.noble_message_service import find_cluster_expert, compute_expert_expertise_for_cluster
    
    noble_messages: Dict[str, Dict[str, Any]] = {}
    message_map = {msg.message_id: msg for msg in question_state.discord_messages}
    
    for cluster in question_state.clusters:
        if not cluster.noble_message_id or cluster.noble_message_id not in message_map:
            continue
            
        noble_msg = message_map[cluster.noble_message_id]
        
        # Find the expert for this cluster
        expert = find_cluster_expert(cluster, message_map)
        
        if expert:
            expert_user_id, expert_username = expert
            # Get expert's profile pic from any of their messages in the cluster
            expert_profile_pic = ""
            for msg_id in cluster.message_ids:
                if msg_id in message_map:
                    msg = message_map[msg_id]
                    if msg.user_id == expert_user_id:
                        expert_profile_pic = msg.profile_pic_url
                        break
            
            # Generate expertise bullet points
            expertise_bullets = await compute_expert_expertise_for_cluster(cluster, question_state)
            
            noble_messages[cluster.label] = {
                "cluster": cluster.label,
                "message_content": noble_msg.content,
                "username": expert_username,
                "bulletpoint": expertise_bullets or [],
                "profile_pic_url": expert_profile_pic,
                "cluster_label": cluster.label,
            }
        else:
            # Fallback if no expert found
            noble_messages[cluster.label] = {
                "cluster": cluster.label,
                "message_content": noble_msg.content,
                "username": noble_msg.username,
                "bulletpoint": [],
                "profile_pic_url": noble_msg.profile_pic_url,
                "cluster_label": cluster.label,
            }
    
    # Try to parse JSON, otherwise keep as string
    try:
        summary_dict = json.loads(summary)
    except json.JSONDecodeError:
        # If not valid JSON, keep as string
        summary_dict = summary
    
    return {
        "results": results,
        "question": question_state.question,
        "summary": summary_dict,
        "noble_messages": noble_messages  # Noble message per cluster
    }
