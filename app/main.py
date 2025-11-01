"""
FastAPI application entry point
"""
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import questions, dashboard, websocket
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
    else:
        print("Warning: DISCORD_BOT_TOKEN not set, skipping Discord bot startup")

