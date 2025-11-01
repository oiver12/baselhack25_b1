"""
Question creation endpoint
"""

import discord
from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from app.api.schemas import QuestionRequest, QuestionResponse, QuestionInfo
from app.config import settings
from app.state import create_question_state, get_active_question
from app.discord_bot.bot import get_bot_instance
from app.services.discord_service import (
    scrape_discord_history,
    send_dm_to_introverted_users,
)
from app.services.question_service import analyze_historical_messages_for_question
from app.services.pipeline import process_all

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse)
async def create_question(request: QuestionRequest) -> QuestionResponse:
    """
    Create a new discussion question

    POST /api/questions
    Body: {"question": "How should we change..."}
    Response: {"question_id": "uuid", "dashboard_url": "..."}
    """
    # Generate unique question ID
    question_id = str(uuid4())
    print(question_id)
    print(request.question)
    
    # Create the question state and set as active question (replaces any existing)
    active_question = create_question_state(question_id, request.question)
    
    # Save to cache
    from app.state import save_all_questions
    save_all_questions()
    
    # Analyze historical messages for relevance in background
    # This will filter messages and add relevant ones to the question
    import asyncio
    asyncio.create_task(_analyze_historical_messages(active_question))
    
    # Post to Discord in background (using bot's event loop)
    _post_to_discord_sync(question_id, request.question)
    
    # Construct dashboard URL
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"
    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url,
    )

async def _analyze_historical_messages(question):
    """Background task to analyze historical messages for the new question"""
    try:
        print(f"Starting historical message analysis for question: {question.question}")
        # Filter historical messages and add relevant ones
        await analyze_historical_messages_for_question(question)
        
        await process_all()
        print(f"Completed historical message analysis for question: {question.question}")
    except Exception as e:
        print(f"Error analyzing historical messages: {e}")
        import traceback
        traceback.print_exc()


def _post_to_discord_sync(question_id: str, question: str):
    """Schedule Discord post in bot's event loop (thread-safe)"""
    import asyncio
    
    bot = get_bot_instance()
    if not bot or not bot.is_ready():
        print("Warning: Bot not ready, skipping Discord post")
        return
    
    # Get the bot's event loop (runs in separate thread)
    bot_loop = bot.loop
    if not bot_loop:
        print("Warning: Bot event loop not available, skipping Discord post")
        return
    
    # Schedule the coroutine in the bot's event loop
    future = asyncio.run_coroutine_threadsafe(
        _post_to_discord(question_id, question),
        bot_loop
    )
    
    # Don't wait for result - fire and forget
    # Errors will be logged inside the coroutine


async def _post_to_discord(question_id: str, question: str):
    """Background task to post the question to Discord"""
    try:
        bot = get_bot_instance()
        if not bot or not bot.is_ready():
            print("Warning: Bot not ready, skipping Discord post")
            return
        
        if not settings.DISCORD_CHANNEL_ID:
            print("Warning: DISCORD_CHANNEL_ID not set, skipping Discord post")
            return
        
        # Get the channel
        channel = bot.get_channel(int(settings.DISCORD_CHANNEL_ID))
        if not channel or not isinstance(channel, discord.TextChannel):
            print(f"Warning: Channel {settings.DISCORD_CHANNEL_ID} not found or not a text channel, skipping Discord post")
            return
        
        # Construct dashboard URL
        dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"
        
        # Create embed (same format as handle_start_discussion)
        embed = discord.Embed(
            title="New discussion started!",
            description=f"**Question:** {question}",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Dashboard",
            value=f"[View live dashboard]({dashboard_url})",
            inline=False,
        )
        embed.add_field(
            name="Status",
            value="Messages in this channel will now be tracked and analyzed.",
            inline=False,
        )
        
        # Send message to channel
        await channel.send(embed=embed)
        print(f"Posted question to Discord channel: {question}")
        
    except Exception as e:
        print(f"Error posting to Discord: {e}")
        import traceback
        traceback.print_exc()


@router.get("/question_and_ids", response_model=List[QuestionInfo])
async def get_question_ids() -> List[QuestionInfo]:
    """
    Get active question ID and question
    
    GET /api/question_and_ids
    Response: List with single QuestionInfo object (or empty if no active question)
    """
    active_question = get_active_question()
    if active_question:
        return [QuestionInfo(question_id=active_question.question_id, question=active_question.question)]
    return []