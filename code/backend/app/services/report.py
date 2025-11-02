"""
Report service for vector analysis and dimension reduction of question answers
"""
from typing import List, Dict, Any
import json
import time
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
    start_time = time.perf_counter()
    
    import asyncio
    from app.services.noble_message_service import (
        compute_noble_messages_for_clusters,
        find_cluster_expert,
        compute_expert_expertise_for_cluster
    )
    
    # Step 1: Create tasks for parallel execution (including noble messages)
    step_start = time.perf_counter()
    results_task = asyncio.create_task(make_2d_plot(question_state))
    
    # Limit messages for summary to avoid token limits (prioritize longer messages)
    all_message_contents = [msg.content for msg in question_state.discord_messages]
    MAX_SUMMARY_MESSAGES = 80  # Reasonable limit for LLM prompt
    
    if len(all_message_contents) > MAX_SUMMARY_MESSAGES:
        # Sort by length (longer = more informative) and take top N
        # Then add a sampling of others to maintain diversity
        sorted_messages = sorted(all_message_contents, key=len, reverse=True)
        selected_messages = sorted_messages[:MAX_SUMMARY_MESSAGES]
        # Optionally add some from different parts of the conversation
        if len(all_message_contents) > MAX_SUMMARY_MESSAGES * 2:
            # Sample every Nth message for diversity
            step = len(all_message_contents) // (MAX_SUMMARY_MESSAGES - len(selected_messages[:60]))
            sampled = [all_message_contents[i] for i in range(0, len(all_message_contents), step)]
            # Combine: top 60 longest + sampled diversity
            selected_messages = sorted_messages[:60] + sampled[:MAX_SUMMARY_MESSAGES - 60]
    else:
        selected_messages = all_message_contents
    
    summary_task = asyncio.create_task(generate_bullet_point_summary_with_pros_cons(
        selected_messages,
        question=question_state.question
    ))
    noble_task = asyncio.create_task(compute_noble_messages_for_clusters(question_state))
    step_delta = time.perf_counter() - step_start
    print(f"[get_whole_Report] Step 1 - Create tasks: {step_delta:.4f}s")
    
    # Step 2: Wait for noble messages (runs in parallel with other tasks)
    step_start = time.perf_counter()
    await noble_task
    step_delta = time.perf_counter() - step_start
    print(f"[get_whole_Report] Step 2 - Compute noble messages: {step_delta:.4f}s")
    
    # Step 3: Gather results from tasks
    step_start = time.perf_counter()
    results, summary = await asyncio.gather(results_task, summary_task)
    step_delta = time.perf_counter() - step_start
    print(f"[get_whole_Report] Step 3 - Gather results and summary: {step_delta:.4f}s")
    
    # Step 4: Build noble messages map with parallelized expert computation
    step_start = time.perf_counter()
    noble_messages: Dict[str, Dict[str, Any]] = {}
    message_map = {msg.message_id: msg for msg in question_state.discord_messages}
    
    # Prepare cluster data and tasks for parallel processing
    cluster_tasks = []
    cluster_data = []
    
    for cluster in question_state.clusters:
        if not cluster.noble_message_id or cluster.noble_message_id not in message_map:
            continue
        
        noble_msg = message_map[cluster.noble_message_id]
        expert = find_cluster_expert(cluster, message_map)
        
        if expert:
            expert_user_id, expert_username = expert
            # Get expert's profile pic (synchronous lookup)
            expert_profile_pic = ""
            for msg_id in cluster.message_ids:
                if msg_id in message_map:
                    msg = message_map[msg_id]
                    if msg.user_id == expert_user_id:
                        expert_profile_pic = msg.profile_pic_url
                        break
            
            # Create task for expertise computation (parallelized, pass message_map to avoid recreating)
            task = asyncio.create_task(compute_expert_expertise_for_cluster(cluster, question_state, message_map))
            cluster_tasks.append(task)
            cluster_data.append((cluster.label, noble_msg, expert_username, expert_profile_pic))
        else:
            # Fallback if no expert found (no async work needed)
            noble_messages[cluster.label] = {
                "cluster": cluster.label,
                "message_content": noble_msg.content,
                "username": noble_msg.username,
                "bulletpoint": [],
                "profile_pic_url": noble_msg.profile_pic_url,
                "cluster_label": cluster.label,
            }
    
    # Wait for all expert expertise computations in parallel using gather
    if cluster_tasks:
        expertise_results = await asyncio.gather(*cluster_tasks)
        
        # Process results
        for (cluster_label, noble_msg, expert_username, expert_profile_pic), expertise_bullets in zip(cluster_data, expertise_results):
            noble_messages[cluster_label] = {
                "cluster": cluster_label,
                "message_content": noble_msg.content,
                "username": expert_username,
                "bulletpoint": expertise_bullets or [],
                "profile_pic_url": expert_profile_pic,
                "cluster_label": cluster_label,
            }
    
    step_delta = time.perf_counter() - step_start
    print(f"[get_whole_Report] Step 4 - Build noble messages map: {step_delta:.4f}s")
    
    # Step 5: Parse JSON summary
    step_start = time.perf_counter()
    try:
        summary_dict = json.loads(summary)
    except json.JSONDecodeError:
        summary_dict = summary
    step_delta = time.perf_counter() - step_start
    print(f"[get_whole_Report] Step 5 - Parse JSON summary: {step_delta:.4f}s")
    
    total_time = time.perf_counter() - start_time
    print(f"[get_whole_Report] Total time: {total_time:.4f}s")
    
    return {
        "results": results,
        "question": question_state.question,
        "summary": summary_dict,
        "noble_messages": noble_messages
    }
