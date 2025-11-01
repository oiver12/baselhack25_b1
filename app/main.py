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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Start Discord bot when FastAPI server starts"""
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
                print(f"✓ Bot connected as {bot.user}")
                break
        else:
            print("Warning: Bot not ready after 30 seconds, skipping historical message fetch")
            return
        
        # Fetch all historical messages and assign them to questions in background (non-blocking)
        async def fetch_history_background():
            print("Fetching historical Discord messages...")
            try:
                messages = await scrape_discord_history()
                print(f"✓ Fetched {len(messages)} historical messages")
                
                # Assign ALL messages to questions immediately
                from app.services.question_service import assign_messages_to_existing_questions
                question_ids = await assign_messages_to_existing_questions(messages)
                print(f"✓ Assigned {len(messages)} messages to {len(question_ids)} questions")
                
                # Process all messages for each question: generate summaries, classify, find excellent
                from app.services.summary_service import process_messages_for_question
                for qid in question_ids:
                    try:
                        await process_messages_for_question(qid)
                        print(f"✓ Processed messages for question {qid}")
                    except Exception as e:
                        print(f"Warning: Failed to process messages for question {qid}: {e}")
                
                # Update question_id field on messages based on assignment
                from app.state import questions as questions_dict
                message_to_question = {}
                for qid, qstate in questions_dict.items():
                    for msg in qstate.discord_messages:
                        message_to_question[msg.message_id] = qid
                
                # Update question_id on all messages
                for msg in messages:
                    if msg.message_id in message_to_question:
                        msg.question_id = message_to_question[msg.message_id]
                
                # Store in global state
                from app.state import global_historical_messages
                from app.state import global_historical_message_ids
                
                # Clear and repopulate
                global_historical_messages.clear()
                global_historical_message_ids.clear()
                global_historical_messages.extend(messages)
                global_historical_message_ids.update(msg.message_id for msg in messages)
                
                print(f"✓ Initialized message ID cache with {len(global_historical_message_ids)} entries")
            except Exception as e:
                print(f"Error fetching historical messages: {e}")
                import traceback
                traceback.print_exc()
        
        # Run in background - don't block startup
        asyncio.create_task(fetch_history_background())
    else:
        print("Warning: DISCORD_BOT_TOKEN not set, skipping Discord bot startup")

