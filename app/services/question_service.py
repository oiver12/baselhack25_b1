"""
Extracting questions from a list of messages and assing messages to questions
"""
from typing import List
from app.state import DiscordMessage, get_question_state, questions, create_question_state
from app.config import settings
from openai import OpenAI
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import uuid


async def extract_asked_questions(messages: List[DiscordMessage]) -> List[str]:
    """
    Extract asked questions from a list of messages.
    All messages starting with "!start_discussion" are considered asked questions.
    """
    asked_questions = set()
    for message in messages:
        if message.content.startswith("!start_discussion"):
            asked_questions.add(message.content)
    return list(asked_questions)

async def assign_one_message_to_existing_questions(message: DiscordMessage, allow_new_questions: bool = True) -> str:
    """
    Assign a single message to an existing question using clustering.
    """
    return await assign_messages_to_existing_questions([message], allow_new_questions)


async def assign_messages_to_existing_questions(messages: [DiscordMessage], allow_new_questions: bool = True) -> List[str]:
    """
    Assign messages to existing questions using clustering.
    First tries to assign to questions extracted from !start_discussion commands,
    then creates up to 3 additional questions from remaining messages (unless <5 messages).
    
    Args:
        messages: List of messages to assign
        allow_new_questions: If False, only map to existing questions, don't create new ones
    
    Returns:
        Final list of question_ids that received messages
    """
    if not messages:
        return []
    
    # Track question IDs that receive messages in this call
    questions_receiving_messages = set()
    
    # First, extract asked questions from !start_discussion commands
    asked_questions_list = await extract_asked_questions(messages)
    asked_questions = {}
    asked_questions_map = {}  # question_text -> question_id
    
    # Create question states for asked questions
    # First, check if questions with this text already exist
    existing_questions_by_text = {qstate.question: qid for qid, qstate in questions.items()}
    
    for asked_q_text in asked_questions_list:
        # Extract the actual question (remove "!start_discussion" prefix)
        question_text = asked_q_text.replace("!start_discussion", "").strip()
        if not question_text:
            continue
        
        # Find the message that contains this question
        question_msg = None
        for msg in messages:
            if msg.content == asked_q_text:
                question_msg = msg
                break
        
        if question_text not in asked_questions_map:
            # Check if a question with this text already exists
            if question_text in existing_questions_by_text:
                # Use existing question
                new_qid = existing_questions_by_text[question_text]
            else:
                # Create new question
                new_qid = str(uuid.uuid4())
                create_question_state(new_qid, question_text)
                # Save to cache
                from app.state import save_all_questions
                save_all_questions()
            
            asked_questions_map[question_text] = new_qid
            asked_questions[new_qid] = {
                'title': question_text,
                'question_id': new_qid,
                'sample_messages': []
            }
        
        qid = asked_questions_map[question_text]
        qstate = get_question_state(qid)
        if question_msg and not any(m.message_id == question_msg.message_id for m in qstate.discord_messages):
            question_msg.question_id = qid  # Set question_id on the message
            qstate.discord_messages.append(question_msg)
            asked_questions[qid]['sample_messages'].append(question_msg.content)
            questions_receiving_messages.add(qid)
    
    # Get all current questions (id and text) and their sample messages (including asked questions)
    current_questions = {qid: get_question_state(qid).question for qid in questions.keys()}
    question_ids_by_text = {v: k for k, v in current_questions.items()}
    
    existing_groups = [asked_questions[qid] for qid in asked_questions.keys()]
    
    all_message_texts = [msg.content for msg in messages]
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Generate embeddings for all messages (with caching)
    if len(all_message_texts) == 0:
        return list(questions_receiving_messages)
    
    from app.services.embedding_cache import get_embeddings_batch
    embeddings = await get_embeddings_batch(all_message_texts, use_cache=True)
    
    # Match messages to existing questions first
    matched_to_existing = {}  # message_idx -> (question_id, question_title)
    unmatched_indices = set(range(len(messages)))
    
    # Build complete list of all existing questions (not just from !start_discussion)
    all_existing_groups = []
    
    # Add asked questions groups
    if existing_groups:
        all_existing_groups.extend(existing_groups)
    
    # Add all other existing questions that aren't in asked_questions
    asked_qids = set(asked_questions.keys())
    for qid, qstate in questions.items():
        if qid not in asked_qids and qstate.discord_messages:
            # Get sample messages from this question
            sample_messages = [msg.content for msg in qstate.discord_messages[:5]]
            all_existing_groups.append({
                'question_id': qid,
                'title': qstate.question,
                'sample_messages': sample_messages
            })
    
    # Match messages to all existing questions
    if all_existing_groups:
        # For each existing question, get representative embeddings
        for group in all_existing_groups:
            if not group['sample_messages']:
                continue
                
            # Get embeddings for sample messages from existing question (with caching)
            from app.services.embedding_cache import get_embeddings_batch
            group_embeddings = await get_embeddings_batch(group['sample_messages'], use_cache=True)
            
            # Calculate similarity between new messages and this group
            similarities = cosine_similarity(embeddings, group_embeddings)
            max_similarities = np.max(similarities, axis=1)  # Max similarity per message
            
            # Match messages with similarity >= 0.5 to this question (lowered to match more to existing)
            # If allow_new_questions is False, use a lower threshold to match more aggressively
            threshold = 0.3 if not allow_new_questions else 0.5
            for msg_idx in list(unmatched_indices):
                if max_similarities[msg_idx] >= threshold:
                    matched_to_existing[msg_idx] = (group['question_id'], group['title'])
                    unmatched_indices.remove(msg_idx)
    
    # Assign matched messages to existing questions
    for msg_idx, (qid, qtitle) in matched_to_existing.items():
        qstate = get_question_state(qid)
        msg = messages[msg_idx]
        # Only add if not already present
        if not any(m.message_id == msg.message_id for m in qstate.discord_messages):
            msg.question_id = qid  # Set question_id on the message
            qstate.discord_messages.append(msg)
            questions_receiving_messages.add(qid)
    
    # Save once after all assignments (if any were made)
    if matched_to_existing:
        from app.state import save_all_questions
        save_all_questions()
    
    # Now cluster only the unmatched messages (if any)
    # Only create new questions if allow_new_questions is True
    if unmatched_indices and allow_new_questions:
        unmatched_list = list(unmatched_indices)
        unmatched_messages = [all_message_texts[i] for i in unmatched_list]
        unmatched_embeddings = embeddings[unmatched_list]
        
        # Determine target number of new questions to create
        # If < 5 messages, be flexible. Otherwise create up to 3 new questions.
        total_messages = len(messages)
        
        if total_messages < 5:
            # Small dataset - be flexible
            target_clusters = max(1, len(unmatched_messages))
        else:
            # Target 3 new questions maximum
            target_clusters = min(3, len(unmatched_messages))
        
        if len(unmatched_messages) == 0:
            # No unmatched messages, nothing to do
            pass
        elif len(unmatched_messages) == 1:
            # Single unmatched message - generate question title for it
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts discussion questions from messages. Generate a clear, concise question title (not a 2-word summary, but a full question like 'How should we improve X?' or 'What is your opinion on Y?'). Respond with only the question title, no explanation."},
                    {"role": "user", "content": f"Extract or create a discussion question from this message:\n{unmatched_messages[0]}"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            question_title = response.choices[0].message.content.strip()
            
            # Create new question
            new_qid = str(uuid.uuid4())
            create_question_state(new_qid, question_title)
            # Save to cache
            from app.state import save_all_questions
            save_all_questions()
            
            # Assign message to new question
            qstate = get_question_state(new_qid)
            msg = messages[unmatched_list[0]]
            msg.question_id = new_qid  # Set question_id on the message
            qstate.discord_messages.append(msg)
            questions_receiving_messages.add(new_qid)
        else:
            # Multiple unmatched messages - cluster them
            # Calculate cosine similarity matrix for unmatched messages
            unmatched_similarity_matrix = cosine_similarity(unmatched_embeddings)
            unmatched_distance_matrix = 1 - unmatched_similarity_matrix
            
            # Use hierarchical clustering targeting the desired number of clusters
            if total_messages < 5:
                # For small datasets, use binary search for minimum meaningful clusters
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
                    
                    # Check if clusters are meaningful (average similarity >= 0.4)
                    valid = True
                    for cluster_id in range(n_clusters):
                        cluster_indices = np.where(cluster_labels == cluster_id)[0]
                        if len(cluster_indices) > 1:
                            cluster_similarities = unmatched_similarity_matrix[np.ix_(cluster_indices, cluster_indices)]
                            avg_similarity = np.mean(cluster_similarities[np.triu_indices_from(cluster_similarities, k=1)])
                            if avg_similarity < 0.4:
                                valid = False
                                break
                    
                    if valid:
                        best_unmatched_clusters = cluster_labels
                        max_clusters = n_clusters
                    else:
                        min_clusters = n_clusters + 1
                
                # If no good clustering found, use default
                if best_unmatched_clusters is None:
                    default_clusters = min(3, len(unmatched_messages))
                    clustering = AgglomerativeClustering(
                        n_clusters=default_clusters,
                        metric='precomputed',
                        linkage='average'
                    )
                    best_unmatched_clusters = clustering.fit_predict(unmatched_distance_matrix)
            else:
                # For larger datasets, directly target 3 clusters
                clustering = AgglomerativeClustering(
                    n_clusters=target_clusters,
                    metric='precomputed',
                    linkage='average'
                )
                best_unmatched_clusters = clustering.fit_predict(unmatched_distance_matrix)
            
            # Group messages by cluster (store indices, not just text)
            unique_unmatched_clusters = np.unique(best_unmatched_clusters)
            unmatched_cluster_groups = {cluster_id: [] for cluster_id in unique_unmatched_clusters}
            for idx, cluster_id in enumerate(best_unmatched_clusters):
                # Store the index in unmatched_list, not the message text
                unmatched_cluster_groups[cluster_id].append(idx)
            
            # Generate question title for each new cluster
            for cluster_id in unique_unmatched_clusters:
                cluster_indices = unmatched_cluster_groups[cluster_id]
                cluster_message_texts = [unmatched_messages[i] for i in cluster_indices]
                
                # Combine messages in cluster for question extraction
                combined_text = "\n".join(cluster_message_texts[:5])
                if len(cluster_message_texts) > 5:
                    combined_text += f"\n... and {len(cluster_message_texts) - 5} more similar messages"
                
                # Add context about existing questions
                existing_context = ""
                if existing_groups:
                    existing_titles = [g['title'] for g in existing_groups]
                    existing_context = f"\n\nNote: There are already these existing questions: {', '.join(existing_titles)}. Only create a new question if these messages don't fit into any of them."
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts discussion questions from messages. Generate a clear, concise question title (not a 2-word summary, but a full question like 'How should we improve X?' or 'What is your opinion on Y?'). Respond with only the question title, no explanation."},
                        {"role": "user", "content": f"Extract or create a discussion question from these messages:\n{combined_text}{existing_context}"}
                    ],
                    max_tokens=50,
                    temperature=0.3
                )
                
                question_title = response.choices[0].message.content.strip()
                
                # Try to match new question title to existing questions (fuzzy matching)
                # Check if the new question title is similar to any existing question
                matched_to_existing_q = False
                if existing_groups:
                    # Get embeddings for the new question title and compare to existing (with caching)
                    from app.services.embedding_cache import get_embedding
                    title_embedding = await get_embedding(question_title)
                    title_embedding = title_embedding.reshape(1, -1)  # Reshape for similarity calculation
                    
                    for group in existing_groups:
                        # Get embedding for existing question title (with caching)
                        existing_title_embedding = await get_embedding(group['title'])
                        existing_title_embedding = existing_title_embedding.reshape(1, -1)
                        
                        # Check similarity
                        similarity = cosine_similarity(title_embedding, existing_title_embedding)[0][0]
                        if similarity >= 0.75:  # High threshold for title matching
                            # Use existing question instead
                            qid = group['question_id']
                            matched_to_existing_q = True
                            break
                
                # Create new question if it doesn't already exist and wasn't matched
                if not matched_to_existing_q:
                    # Check if question already exists by text
                    if question_title in question_ids_by_text:
                        qid = question_ids_by_text[question_title]
                    else:
                        new_qid = str(uuid.uuid4())
                        create_question_state(new_qid, question_title)
                        qid = new_qid
                        # Save to cache
                        from app.state import save_all_questions
                        save_all_questions()
                elif matched_to_existing_q:
                    pass  # qid already set above
                else:
                    qid = question_ids_by_text[question_title]
                
                qstate = get_question_state(qid)
                
                # Assign all messages in this cluster to the question
                for idx_in_unmatched in cluster_indices:
                    # Get the original message index
                    msg_idx = unmatched_list[idx_in_unmatched]
                    msg = messages[msg_idx]
                    # Only add if not already present
                    if not any(m.message_id == msg.message_id for m in qstate.discord_messages):
                        msg.question_id = qid  # Set question_id on the message
                        qstate.discord_messages.append(msg)
                        questions_receiving_messages.add(qid)
                
                # Save once after all messages in this cluster are assigned
                if cluster_indices:
                    from app.state import save_all_questions
                    save_all_questions()
    
    return list(questions_receiving_messages)
