"""
Consensus detection service
Monitors clusters and detects when consensus is reached
"""
from typing import Dict, List, Optional, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from app.state import QuestionState, DiscordMessage, get_question_state
from app.config import settings
from app.services.solution_service import analyze_cluster


async def get_total_guild_members(question_id: str) -> int:
    """
    Get total number of non-bot members in the Discord guild
    
    Args:
        question_id: The question ID (to find a message and get channel/guild)
        
    Returns:
        Total number of non-bot members in the guild, or 0 if unable to determine
    """
    from app.discord_bot.bot import get_bot_instance
    
    bot = get_bot_instance()
    if not bot or not bot.is_ready():
        return 0
    
    question_state = get_question_state(question_id)
    if not question_state or not question_state.discord_messages:
        return 0
    
    # Get channel_id from first message
    first_message = question_state.discord_messages[0]
    channel_id = first_message.channel_id
    
    try:
        # Get channel from bot
        channel = bot.get_channel(int(channel_id))
        if not channel:
            return 0
        
        # Get guild from channel
        guild = channel.guild
        if not guild:
            return 0
        
        # Get all non-bot members
        members = [member for member in guild.members if not member.bot]
        print(f"Total guild members: {len(members)}")
        return len(members)
    except Exception as e:
        print(f"Error getting guild members: {e}")
        return 0


async def compute_cluster_metrics(
    cluster_messages: List[DiscordMessage],
    all_question_messages: List[DiscordMessage],
    question_state: QuestionState,
    total_guild_members: int = 0,
) -> Dict[str, float]:
    """
    Compute metrics for a cluster to determine if consensus is reached
    
    Args:
        cluster_messages: Messages in this cluster
        all_question_messages: All messages for the question
        question_state: The question state
        total_guild_members: Total number of non-bot members in the Discord guild (0 if unknown)
        
    Returns:
        Dictionary with metrics: cluster_size_ratio, user_ratio, sentiment_std, intra_similarity
    """
    if not cluster_messages or not all_question_messages:
        return {
            "cluster_size_ratio": 0.0,
            "user_ratio": 0.0,
            "sentiment_std": 1.0,
            "intra_similarity": 0.0,
        }
    
    # 1. cluster_size_ratio = len(cluster.messages) / len(all_question_messages)
    cluster_size_ratio = len(cluster_messages) / len(all_question_messages)
    
    # 2. user_ratio = unique_users_in_cluster / total_users_in_guild
    unique_users_in_cluster = len(set(msg.user_id for msg in cluster_messages))
    
    # Use total_guild_members if provided, otherwise fall back to participants who wrote
    if total_guild_members > 0:
        total_users = total_guild_members
    else:
        # Fallback to participants who have written messages
        total_users = len(question_state.participants)
    
    user_ratio = unique_users_in_cluster / max(1, total_users)
    
    # 3. sentiment_std = std(sentiments in cluster)
    # Map classifications to numeric values: "good"=1, "neutral"=0, "bad"=-1
    sentiment_map = {"good": 1.0, "neutral": 0.0, "bad": -1.0}
    sentiments = [
        sentiment_map.get(msg.classification or "neutral", 0.0)
        for msg in cluster_messages
    ]
    sentiment_std = float(np.std(sentiments)) if sentiments else 1.0
    
    # 4. intra_similarity = avg pairwise cosine similarity inside cluster
    # Get embeddings for cluster messages
    client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    intra_similarity = 0.0
    
    if client and len(cluster_messages) > 1:
        try:
            from app.services.embedding_cache import get_embeddings_batch
            cluster_texts = [msg.content for msg in cluster_messages]
            embeddings = await get_embeddings_batch(cluster_texts, use_cache=True)
            
            # Calculate pairwise cosine similarities
            similarity_matrix = cosine_similarity(embeddings)
            # Get upper triangle (avoid duplicates and diagonal)
            triu_indices = np.triu_indices_from(similarity_matrix, k=1)
            similarities = similarity_matrix[triu_indices]
            
            intra_similarity = float(np.mean(similarities)) if len(similarities) > 0 else 0.0
        except Exception as e:
            print(f"Error computing intra_similarity: {e}")
            intra_similarity = 0.0
    elif len(cluster_messages) == 1:
        intra_similarity = 1.0  # Single message has perfect similarity with itself
    
    return {
        "cluster_size_ratio": cluster_size_ratio,
        "user_ratio": user_ratio,
        "sentiment_std": sentiment_std,
        "intra_similarity": intra_similarity,
    }


def check_consensus_conditions(metrics: Dict[str, float]) -> bool:
    """
    Check if consensus conditions are met
    
    Args:
        metrics: Dictionary with cluster metrics
        
    Returns:
        True if all consensus conditions are met
    """
    # Consensus condition (trigger threshold):
    # - cluster_size_ratio ≥ 0.45
    # - user_ratio ≥ 0.50
    # - sentiment_std ≤ 0.25
    # - intra_similarity ≥ 0.55
    
    return (
        metrics["cluster_size_ratio"] >= 0.45
        and metrics["user_ratio"] >= 0.50
        and metrics["sentiment_std"] <= 0.25
        and metrics["intra_similarity"] >= 0.55
    )


async def detect_consensus_for_question(question_id: str) -> List[Dict[str, Any]]:
    """
    Detect consensus for all clusters in a question
    
    Args:
        question_id: The question ID to check
        
    Returns:
        List of consensus events (empty if none detected)
    """
    question_state = get_question_state(question_id)
    if not question_state or not question_state.discord_messages:
        return []
    
    all_messages = question_state.discord_messages
    
    # Get total guild members (all users in the Discord server, not just those who wrote)
    total_guild_members = await get_total_guild_members(question_id)
    
    # Group messages by their 2-word summary (cluster label)
    clusters: Dict[str, List[DiscordMessage]] = {}
    for msg in all_messages:
        if msg.two_word_summary:
            cluster_label = msg.two_word_summary
            if cluster_label not in clusters:
                clusters[cluster_label] = []
            clusters[cluster_label].append(msg)
    
    consensus_events = []
    
    # Check each cluster for consensus
    for cluster_label, cluster_messages in clusters.items():
        # Skip if cluster is too small
        if len(cluster_messages) < 2:
            continue
        
        # Compute metrics
        metrics = await compute_cluster_metrics(
            cluster_messages=cluster_messages,
            all_question_messages=all_messages,
            question_state=question_state,
            total_guild_members=total_guild_members,
        )
        
        # Check consensus conditions
        if check_consensus_conditions(metrics):
            # Call solution analysis pipeline
            solution = await analyze_cluster(
                question_id=question_id,
                cluster_label=cluster_label,
                cluster_messages=cluster_messages,
                cluster_metrics=metrics,
            )
            
            if solution:
                # Emit consensus detected event
                event = {
                    "event": "consensus_detected",
                    "payload": {
                        "question_id": question_id,
                        "cluster_label": cluster_label,
                        "solution": solution.get("text", ""),
                        "confidence": solution.get("confidence", 0.0),
                        "participants": solution.get("participants", []),
                        "metrics": metrics,
                    },
                }
                consensus_events.append(event)
    
    return consensus_events


async def check_and_broadcast_consensus(question_id: str) -> None:
    """
    Check for consensus and broadcast events if detected
    
    Args:
        question_id: The question ID to check
    """
    consensus_events = await detect_consensus_for_question(question_id)
    
    # Broadcast events via WebSocket
    if consensus_events:
        from app.api.routes.websocket import broadcast_consensus_event
        
        for event in consensus_events:
            await broadcast_consensus_event(question_id, event["payload"])

