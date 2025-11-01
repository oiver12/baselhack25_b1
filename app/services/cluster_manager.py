import numpy as np
from uuid import uuid4
from app.services import clustering, llm_service
from app.state import get_active_question, save_all_questions, Cluster
from app.services.embedding_cache import get_embeddings_batch, get_embedding
from app.config import settings
from sklearn.cluster import KMeans


async def assign_message(message):
    q = get_active_question()
    if not q:
        return
    emb = await get_embedding(message.content)
    idx = clustering.assign_nearest(emb, q.clusters, settings.CLUSTER_ASSIGNMENT_THRESHOLD)
    if idx is not None:
        c = q.clusters[idx]
        c.message_ids.append(message.message_id)
        message.two_word_summary = c.label
        texts = [m.content for m in q.discord_messages if m.message_id in c.message_ids]
        embs = await get_embeddings_batch(texts, use_cache=True)
        c.centroid = clustering.centroid(embs).tolist()
        c.intra_sim = clustering.intra_similarity(embs)
    else:
        q.unassigned_buffer.append(message.message_id)
    save_all_questions()


async def bootstrap_fixed_kmeans():
    """
    Bootstrap clustering using fixed KMeans with k clusters.
    Uses cached embeddings, L2-normalizes them, and generates labels only for new clusters.
    """
    k = settings.CLUSTER_MAX_COUNT
    q = get_active_question()
    if not q or not q.discord_messages:
        return
    
    messages = q.discord_messages
    if len(messages) < k:
        # Not enough messages for k clusters
        return
    
    # Fetch embeddings (cached)
    texts = [m.content for m in messages]
    embs = await get_embeddings_batch(texts, use_cache=True)
    
    # L2-normalize embeddings
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
    embs_normalized = embs / norms
    
    # Run KMeans
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embs_normalized)
    
    # Create new clusters
    new_clusters = []
    generated_labels = []  # Track labels generated so far in this loop
    
    for cluster_id in range(k):
        cluster_indices = np.where(cluster_labels == cluster_id)[0]
        if len(cluster_indices) == 0:
            continue
        
        cluster_messages = [messages[i] for i in cluster_indices]
        cluster_embs = embs[cluster_indices]  # Use original (not normalized) for centroid
        
        # Compute centroid (from original embeddings)
        centroid = clustering.centroid(cluster_embs)
        
        # Compute intra-cluster similarity (from original embeddings)
        intra_sim = clustering.intra_similarity(cluster_embs)
        
        # Compute sentiment metrics
        sentiment = clustering.sentiment_metrics(cluster_messages)
        
        # Try to find existing cluster with similar messages for label reuse
        cluster_msg_ids = {m.message_id for m in cluster_messages}
        matching_existing = None
        
        # Find the most overlapping existing cluster
        best_overlap_ratio = 0.0
        for existing_cluster in q.clusters:
            existing_msg_ids = set(existing_cluster.message_ids)
            # Check overlap ratio (>50% of smaller cluster)
            overlap = len(cluster_msg_ids & existing_msg_ids)
            min_size = min(len(cluster_msg_ids), len(existing_msg_ids))
            if min_size > 0:
                overlap_ratio = overlap / min_size
                if overlap_ratio > 0.5 and overlap_ratio > best_overlap_ratio:
                    best_overlap_ratio = overlap_ratio
                    matching_existing = existing_cluster
        
        # Use existing label if significant overlap found, otherwise generate new
        if matching_existing and best_overlap_ratio > 0.5:
            label = matching_existing.label
        else:
            # Generate new label (use up to 5 messages)
            # Pass existing labels from this batch to ensure distinctness
            label_texts = [m.content for m in cluster_messages[:5]]
            label = await llm_service.two_word_label(label_texts, existing_labels=generated_labels)
        
        # Track this label for subsequent clusters (both reused and newly generated)
        generated_labels.append(label)
        
        # Create cluster
        new_cluster = Cluster(
            cluster_id=str(uuid4()),
            label=label,
            centroid=centroid.tolist(),
            message_ids=[m.message_id for m in cluster_messages],
            frozen=False,
            intra_sim=intra_sim,
            sentiment_avg=sentiment["avg"],
            sentiment_std=sentiment["std"],
        )
        new_clusters.append(new_cluster)
    
    # Replace all existing clusters
    q.clusters = new_clusters
    for c in new_clusters:
        print(f"Cluster {c.label} created with {len(c.message_ids)} messages")
    
    # Update message.two_word_summary from cluster assignments
    cluster_by_msg_id = {msg_id: cluster for cluster in new_clusters for msg_id in cluster.message_ids}
    for msg in messages:
        if msg.message_id in cluster_by_msg_id:
            msg.two_word_summary = cluster_by_msg_id[msg.message_id].label
    
    # Update two_word_summaries list
    q.two_word_summaries = sorted({c.label for c in new_clusters})
    
    # Clear unassigned_buffer (all messages are now assigned)
    q.unassigned_buffer = []
    
    save_all_questions()