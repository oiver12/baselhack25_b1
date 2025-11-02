"""
Service for finding noble messages per cluster and identifying cluster experts
"""
from typing import Optional, Dict, Tuple, List
from collections import Counter
from app.state import QuestionState, Cluster, DiscordMessage, save_all_questions
from app.services.llm_service import noble_message_per_cluster, generate_expert_expertise_bullets


async def compute_noble_messages_for_clusters(question_state: QuestionState, save_state: bool = True) -> None:
    """
    Compute and store noble message ID for each cluster in the question state.
    Parallelized for faster execution.
    
    Updates the noble_message_id field for each cluster.
    
    Args:
        question_state: The question state containing clusters and messages
        save_state: Whether to save the state after computing (default: True)
    """
    if not question_state.clusters:
        return
    
    # Create a lookup map for messages by ID
    message_map: dict[str, DiscordMessage] = {
        msg.message_id: msg for msg in question_state.discord_messages
    }
    
    # Prepare tasks for parallel execution
    import asyncio
    tasks = []
    cluster_list = []
    
    for cluster in question_state.clusters:
        if not cluster.message_ids:
            continue
        
        # Get message contents for this cluster
        cluster_messages = [
            message_map[msg_id].content 
            for msg_id in cluster.message_ids 
            if msg_id in message_map
        ]
        
        if not cluster_messages:
            continue
        
        # Skip if already computed
        if cluster.noble_message_id:
            continue
        
        # Create task for parallel execution
        task = asyncio.create_task(noble_message_per_cluster(
            cluster_messages, 
            cluster_label=cluster.label
        ))
        tasks.append(task)
        cluster_list.append(cluster)
    
    # Wait for all tasks in parallel using gather
    if tasks:
        noble_contents = await asyncio.gather(*tasks)
        
        # Process results
        computed_count = 0
        for cluster, noble_content in zip(cluster_list, noble_contents):
            if noble_content:
                # Find the message ID that matches this content
                for msg_id in cluster.message_ids:
                    if msg_id in message_map and message_map[msg_id].content == noble_content:
                        cluster.noble_message_id = msg_id
                        computed_count += 1
                        break
    else:
        computed_count = 0
    
    # Save state if any noble messages were computed
    if computed_count > 0 and save_state:
        save_all_questions()


def find_cluster_expert(
    cluster: Cluster, 
    message_map: Dict[str, DiscordMessage]
) -> Optional[Tuple[str, str]]:
    """
    Find the expert for a cluster (user with most messages, or noble message author).
    
    Args:
        cluster: The cluster to analyze
        message_map: Map of message_id -> DiscordMessage
        
    Returns:
        Tuple of (user_id, username) of the expert, or None if no messages
    """
    if not cluster.message_ids:
        return None
    
    # Count messages per user in this cluster
    user_counts: Counter[str] = Counter()
    user_info: Dict[str, Tuple[str, str]] = {}  # user_id -> (user_id, username)
    
    for msg_id in cluster.message_ids:
        if msg_id in message_map:
            msg = message_map[msg_id]
            user_counts[msg.user_id] += 1
            if msg.user_id not in user_info:
                user_info[msg.user_id] = (msg.user_id, msg.username)
    
    if not user_counts:
        return None
    
    # If there's a noble message, prefer that user (they wrote the best message)
    if cluster.noble_message_id and cluster.noble_message_id in message_map:
        noble_msg = message_map[cluster.noble_message_id]
        return (noble_msg.user_id, noble_msg.username)
    
    # Otherwise, return user with most messages
    expert_user_id = user_counts.most_common(1)[0][0]
    return user_info[expert_user_id]


async def compute_expert_expertise_for_cluster(
    cluster: Cluster,
    question_state: QuestionState,
    message_map: Optional[Dict[str, DiscordMessage]] = None
) -> Optional[List[str]]:
    """
    Compute expertise bullet points for the cluster expert.
    
    Args:
        cluster: The cluster to analyze
        question_state: The question state containing all messages
        message_map: Optional pre-built message map (for optimization)
        
    Returns:
        List of 3 expertise bullet points, or None if no expert found
    """
    if message_map is None:
        message_map = {msg.message_id: msg for msg in question_state.discord_messages}
    expert = find_cluster_expert(cluster, message_map)
    
    if not expert:
        return None
    
    expert_user_id, expert_username = expert
    
    # Get all messages from this expert in this cluster
    expert_messages = [
        message_map[msg_id].content
        for msg_id in cluster.message_ids
        if msg_id in message_map and message_map[msg_id].user_id == expert_user_id
    ]
    
    if not expert_messages:
        return None
    
    # Generate expertise bullet points
    bullets = await generate_expert_expertise_bullets(
        expert_messages,
        cluster_label=cluster.label
    )
    
    return bullets

