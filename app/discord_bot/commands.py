"""
Discord bot command handlers
"""

import httpx
import discord
from app.config import settings


async def handle_start_discussion(message: discord.Message, question: str, bot):
    """
    Handle the !start_discussion command

    Creates a question via API and posts response in Discord

    Args:
        message: Discord message object
        question: The question text
        bot: The bot instance to register the channel
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

            # Register this channel for the discussion
            channel_id = str(message.channel.id)
            bot.active_discussions[channel_id] = question_id

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
            embed.add_field(
                name="Status",
                value="Messages in this channel will now be tracked and analyzed.",
                inline=False,
            )

            await message.reply(embed=embed)

        except httpx.HTTPError as e:
            await message.reply(f"Error creating discussion: {e}")
        except Exception as e:
            await message.reply(f"Unexpected error: {e}")
