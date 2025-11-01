"""
Report endpoint for getting whole report with 2D visualization and summary
"""
import io
import discord
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.state import get_active_question
from app.services.report import get_whole_Report
from app.services.reportPDF import generate_pdf_report
from app.discord_bot.bot import get_bot_instance
from app.config import settings

router = APIRouter()


@router.get("/report/{question_id}")
async def get_report(question_id: str):
    """
    Get the whole report for a question including 2D coordinates and summary
    
    GET /api/report/{question_id}
    Response: {
        "results": [
            {
                "message_id": str,
                "x": float,
                "y": float,
                "message": str,
                "name": str,
                "profile_pic_url": str
            }
        ],
        "summary": {
            "summary": str,
            "points": [...]
        }
    }
    """
    question_state = get_active_question()
    
    if not question_state:
        raise HTTPException(status_code=404, detail="No active question")
    
    # Verify question_id matches active question
    if question_state.question_id != question_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get the whole report
    report = await get_whole_Report(question_state)
    
    # Generate PDF and send to Discord in background (using bot's event loop)
    _send_pdf_to_discord_sync(question_id, question_state)
    
    return report


def _send_pdf_to_discord_sync(question_id: str, question_state):
    """Schedule PDF generation and Discord post in bot's event loop (thread-safe)"""
    import asyncio
    
    bot = get_bot_instance()
    if not bot or not bot.is_ready():
        print("Warning: Bot not ready, skipping PDF Discord post")
        return
    
    # Get the bot's event loop (runs in separate thread)
    bot_loop = bot.loop
    if not bot_loop:
        print("Warning: Bot event loop not available, skipping PDF Discord post")
        return
    
    # Schedule the coroutine in the bot's event loop
    future = asyncio.run_coroutine_threadsafe(
        _send_pdf_to_discord(question_id, question_state),
        bot_loop
    )
    
    # Don't wait for result - fire and forget
    # Errors will be logged inside the coroutine


async def _send_pdf_to_discord(question_id: str, question_state):
    """Background task to generate PDF and send to Discord"""
    try:
        # Generate PDF
        pdf_bytes = await generate_pdf_report(question_state)
        
        # Send to Discord
        bot = get_bot_instance()
        if not bot or not bot.is_ready():
            print("Warning: Bot not ready, skipping PDF Discord post")
            return
        
        if not settings.DISCORD_CHANNEL_ID:
            print("Warning: DISCORD_CHANNEL_ID not set, skipping PDF Discord post")
            return
        
        # Get the channel
        channel = bot.get_channel(int(settings.DISCORD_CHANNEL_ID))
        if not channel or not isinstance(channel, discord.TextChannel):
            print(f"Warning: Channel {settings.DISCORD_CHANNEL_ID} not found or not a text channel, skipping PDF Discord post")
            return
        
        # Create file object
        pdf_file = discord.File(
            io.BytesIO(pdf_bytes),
            filename=f"report_{question_id}.pdf"
        )
        
        # Send to Discord
        await channel.send(
            content=f"📊 Report generated for: **{question_state.question}**",
            file=pdf_file
        )
        print(f"Posted PDF report to Discord channel: {question_state.question}")
        
    except Exception as e:
        print(f"Error generating/sending PDF to Discord: {e}")
        import traceback
        traceback.print_exc()


@router.get("/report/{question_id}/pdf")
async def get_report_pdf(question_id: str):
    """
    Get PDF report directly (for iterative testing)
    
    GET /api/report/{question_id}/pdf
    Returns: PDF file (viewable in browser)
    """
    question_state = get_active_question()
    
    if not question_state:
        raise HTTPException(status_code=404, detail="No active question")
    
    # Verify question_id matches active question
    if question_state.question_id != question_id:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Generate PDF
    pdf_bytes = await generate_pdf_report(question_state)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="report_{question_id}.pdf"'
        }
    )

