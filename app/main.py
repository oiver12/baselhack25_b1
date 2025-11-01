"""
FastAPI application entry point
"""
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import questions, dashboard, websocket, messages
from app.config import settings
from app.discord_bot.bot import run_bot

app = FastAPI(title="BaselHack25 Consensus Builder API")

# CORS middleware (more permissive and logs CORS settings for debugging)
import logging

logger = logging.getLogger("uvicorn")

logger.info(f"Configuring CORS: allow_origins={settings.CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Optionally expose all headers
    max_age=600,           # Cache preflight responses for 10 minutes
)


# Include routers
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "BaselHack25 Consensus Builder API"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Load persisted cache and start Discord bot when FastAPI server starts"""
    from app.state import (
        load_all_discord_messages, 
        load_all_questions, 
        global_historical_messages,
        get_newest_cached_message_timestamp
    )
    
    # Load persisted cache first
    print("\n" + "="*60)
    print("STARTING UP - Loading persisted cache...")
    print("="*60)
    load_all_discord_messages()  # Load Discord messages
    load_all_questions()  # Load questions
    
    # Determine scrape mode
    cached_message_count = len(global_historical_messages)
    newest_timestamp = get_newest_cached_message_timestamp()
    
    if cached_message_count > 0:
        print(f"Cache status: {cached_message_count} messages loaded")
        if newest_timestamp:
            print(f"Newest cached message: {newest_timestamp.isoformat()}")
            print(f"Startup mode: INCREMENTAL (will fetch only new messages)")
        else:
            print(f"Startup mode: FULL (cache exists but no timestamp found)")
            newest_timestamp = None
    else:
        print(f"Cache status: Empty - no cached messages found")
        print(f"Startup mode: FULL (initial scrape)")
        newest_timestamp = None
    
    if settings.DISCORD_BOT_TOKEN:
        # Run Discord bot in a separate thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("Discord bot thread started")
        
        # Wait for bot to be ready, then fetch historical messages
        import asyncio
        from app.discord_bot.bot import get_bot_instance
        from app.services.discord_service import scrape_discord_history
        
        # Wait for bot to connect (up to 30 seconds)
        print("Waiting for bot to connect...")
        for _ in range(60):  # 60 * 0.5s = 30s
            await asyncio.sleep(0.5)
            bot = get_bot_instance()
            if bot and bot.is_ready():
                print(f"Bot connected as {bot.user}")
                break
        else:
            print("Warning: Bot not ready after 30 seconds, skipping historical message fetch")
            return
        
        # Fetch messages (incremental or full) in background (non-blocking)
        async def fetch_history_background():
            print("\n" + "="*60)
            print("FETCHING DISCORD MESSAGES")
            print("="*60)
            try:
                # Fetch messages (newest_timestamp determines mode)
                new_messages = await scrape_discord_history(after=newest_timestamp)
                
                if new_messages:
                    print(f"\nFetched {len(new_messages)} new messages")
                    
                    # Assign new messages to questions
                    from app.services.question_service import assign_messages_to_existing_questions
                    question_ids = await assign_messages_to_existing_questions(new_messages)
                    print(f"Assigned {len(new_messages)} messages to {len(question_ids)} questions")
                    
                    # Process all messages for each question: generate summaries, classify, find excellent
                    from app.services.summary_service import process_messages_for_question
                    for qid in question_ids:
                        try:
                            await process_messages_for_question(qid)
                            print(f"Processed messages for question {qid}")
                        except Exception as e:
                            print(f"Warning: Failed to process messages for question {qid}: {e}")
                    
                    # Update question_id field on messages based on assignment
                    from app.state import questions as questions_dict
                    message_to_question = {}
                    for qid, qstate in questions_dict.items():
                        for msg in qstate.discord_messages:
                            message_to_question[msg.message_id] = qid
                    
                    # Update question_id on all messages
                    for msg in new_messages:
                        if msg.message_id in message_to_question:
                            msg.question_id = message_to_question[msg.message_id]
                    
                    # Merge with existing cache
                    from app.state import (
                        global_historical_messages, 
                        global_historical_message_ids, 
                        save_all_discord_messages, 
                        save_all_questions
                    )
                    
                    # Add new messages (avoid duplicates)
                    existing_ids = set(global_historical_message_ids)
                    added_count = 0
                    for msg in new_messages:
                        if msg.message_id not in existing_ids:
                            global_historical_messages.append(msg)
                            global_historical_message_ids.add(msg.message_id)
                            added_count += 1
                    
                    # Save updated cache
                    save_all_discord_messages()
                    save_all_questions()
                    
                    print(f"\nUpdated cache: Added {added_count} new messages")
                    print(f"Total messages in cache: {len(global_historical_messages)}")
                else:
                    print(f"\nNo new messages found - cache is up to date")
                    print(f"Total messages in cache: {cached_message_count}")
                
                print("="*60)
                print("STARTUP COMPLETE")
                print("="*60 + "\n")
            except Exception as e:
                print(f"\nError fetching historical messages: {e}")
                import traceback
                traceback.print_exc()
        
        # Run in background - don't block startup
        asyncio.create_task(fetch_history_background())
    else:
        print("Warning: DISCORD_BOT_TOKEN not set, skipping Discord bot startup")

