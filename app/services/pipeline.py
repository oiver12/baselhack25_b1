import asyncio
from app.config import settings
from app.services import cluster_manager, llm_service
from app.state import get_active_question, save_all_questions


async def process_all():
    q = get_active_question()
    if not q or not q.discord_messages:
        return
    if not q.clusters:
        await cluster_manager.bootstrap_fixed_kmeans()

    for m in q.discord_messages:
        if not m.classification:
            m.classification = await llm_service.classify_message(m.content)

    good_msgs = [m.content for m in q.discord_messages if m.classification == "good"]
    q.excellent_message = await llm_service.best_message(good_msgs)
    for m in q.discord_messages:
        m.is_excellent = m.content == q.excellent_message
    save_all_questions()


async def process_one(message):
    await cluster_manager.assign_message(message)
    q = get_active_question()
    if not message.classification:
        message.classification = await llm_service.classify_message(message.content)
    save_all_questions()


async def periodic_clustering():
    """
    Background task that runs bootstrap_fixed_kmeans() periodically.
    Skips iteration if message count hasn't changed since last run.
    """
    interval = settings.CLUSTER_PERIODIC_INTERVAL
    last_message_count = 0
    
    while True:
        try:
            print("Periodic clustering")
            q = get_active_question()
            if not q or not q.discord_messages:
                await asyncio.sleep(interval)
                continue
            
            current_count = len(q.discord_messages)
            
            # Skip if message count hasn't changed
            if current_count == last_message_count:
                await asyncio.sleep(interval)
                continue
            
            # Update count and run clustering
            last_message_count = current_count
            
            # Only run if we have at least 4 messages (k=4)
            if current_count >= 4:
                await cluster_manager.bootstrap_fixed_kmeans()
                print(f"Clustering: Updated {len(q.clusters)} clusters from {current_count} messages")
            else:
                print(f"Clustering: Skipping ({current_count} messages < 4)")
            
        except Exception as e:
            print(f"Clustering: Error - {e}")
        
        await asyncio.sleep(interval)