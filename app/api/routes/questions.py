"""
Question creation endpoint
"""

from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from app.api.schemas import QuestionRequest, QuestionResponse
from app.config import settings
from app.state import create_question_state, questions, global_historical_messages
from app.services.discord_service import (
    scrape_discord_history,
    send_dm_to_introverted_users,
)

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
    
    # Create question state
    create_question_state(question_id, request.question)
    
    # Fetch historical messages and assign them to questions
    from app.services.question_service import assign_messages_to_existing_questions
    from app.services.discord_service import scrape_discord_history
    
    try:
        # Get all messages from Discord
        messages = await scrape_discord_history()
        
        # Assign messages to questions (including the new one)
        await assign_messages_to_existing_questions(messages)
    except Exception as e:
        print(f"Warning: Could not fetch and assign messages: {e}")
        import traceback
        traceback.print_exc()
    
    # Post the new question to Discord with embed response (like handle_start_discussion does)
    from app.discord_bot.bot import get_bot_instance
    import asyncio
    import discord
    bot = get_bot_instance()
    
    # Construct dashboard URL
    dashboard_url = f"{settings.DASHBOARD_BASE_URL}/{question_id}"
    
    if bot and bot.is_ready():
        # Need to run in bot's event loop, not FastAPI's loop
        bot_loop = bot.loop
        current_loop = asyncio.get_event_loop()
        
        async def _post_question_response():
            posted = False
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages and not posted:
                        # Post embed response exactly like handle_start_discussion does
                        embed = discord.Embed(
                            title="New discussion started!",
                            description=f"**Question:** {request.question}",
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
                        
                        await channel.send(embed=embed)
                        
                        # Register this channel for the discussion (like handle_start_discussion does)
                        channel_id = str(channel.id)
                        bot.active_discussions[channel_id] = question_id
                        
                        posted = True
                        break
                if posted:
                    break
            return posted
        
        if bot_loop != current_loop:
            # Run in bot's event loop using run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(_post_question_response(), bot_loop)
            try:
                future.result(timeout=10)  # 10 second timeout
            except Exception as e:
                print(f"Warning: Failed to post question to Discord: {e}")
        else:
            # Already in bot's loop, run directly
            await _post_question_response()
    else:
        print("Warning: Bot not available or not ready to post question to Discord.")

    return QuestionResponse(
        question_id=question_id,
        dashboard_url=dashboard_url,
    )

@router.get("/question_ids", response_model=List[str])
async def get_question_ids() -> List[str]:
    """
    Get all question IDs

    GET /api/question_ids
    Response: List of question IDs
    """
    return list(questions.keys())