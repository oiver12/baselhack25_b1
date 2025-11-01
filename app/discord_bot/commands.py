"""
Discord bot command handlers
"""
import httpx
from discord.ext import commands
from app.config import settings


async def handle_start_discussion(ctx: commands.Context, question: str):
    """
    Handle the !start_discussion command
    
    Creates a question via API and posts response in Discord
    
    Args:
        ctx: Discord context
        question: The question text
    """
    # Call backend API to create question
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://localhost:8000/api/questions",
                json={"question": question},
            )
            response.raise_for_status()
            data = response.json()
            
            question_id = data["question_id"]
            dashboard_url = data["dashboard_url"]
            
            # Post in Discord
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
            
            await ctx.send(embed=embed)
            
        except httpx.HTTPError as e:
            await ctx.send(f"Error creating discussion: {e}")
        except Exception as e:
            await ctx.send(f"Unexpected error: {e}")

