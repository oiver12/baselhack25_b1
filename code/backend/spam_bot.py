import os
import asyncio
import discord
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_SPAMBOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
MESSAGES_PER_SECOND = 5  # adjust speed here

client = discord.Client(intents=discord.Intents.default(), guild_id=GUILD_ID)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

if not DISCORD_TOKEN or not OPENAI_API_KEY or not GUILD_ID or not CHANNEL_ID:
    raise ValueError("Missing environment variables")


async def generate_answers(question: str, n: int = 100):
    """Generate n diverse answers using ChatGPT in small buckets."""
    print("Generating answers...")
    answers = []
    batch_size = 10
    for i in range(0, n, batch_size):
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Give distinct, short, opinion-style answers."
            }, {
                "role": "user",
                "content": f"Question: {question}\nGive {batch_size} very different short answers."
            }],
            temperature=1.0
        )
        text = response.choices[0].message.content.strip()
        for line in text.split("\n"):
            if line.strip():
                answers.append(line.strip("-• "))
    print(f"Collected {len(answers)} answers.")
    return answers[:n]


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(int(CHANNEL_ID))

    # Ask for input
    question = input("Enter your question: ")
    answers = await generate_answers(question, 100)

    delay = 1.0 / MESSAGES_PER_SECOND
    print(f"Starting to spam {len(answers)} messages at {MESSAGES_PER_SECOND} msg/s...")

    for i, msg in enumerate(answers):
        await channel.send(f"{msg}")
        await asyncio.sleep(delay)

    print("Done sending messages.")
    await client.close()


client.run(DISCORD_TOKEN)
