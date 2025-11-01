# BaselHack25 Consensus Builder Backend

Discord bot backend for building consensus through AI analysis of discussions. This project is part of the [BaselHack 2025 Collective Intelligence Challenge](https://www.baselhack.ch/challenges/collective-intelligence-building-consensus-through-ai).

## Overview

A Discord bot integrated with a Python FastAPI backend that:
- Creates discussion sessions from questions
- Analyzes Discord chat history for relevant information
- Generates live consensus views with pros/cons
- Shows real-time message summaries on a dashboard
- Sends DMs to introverted users to gather their views

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point (auto-starts Discord bot)
├── config.py               # Configuration settings
├── state.py                # In-memory state management (no database)
├── api/
│   ├── schemas.py          # Pydantic models (matches TypeScript types)
│   └── routes/
│       ├── questions.py    # POST /api/questions
│       ├── dashboard.py    # GET /api/dashboard/:question_id
│       └── websocket.py    # WS /ws/:question_id
├── services/
│   ├── discord_service.py  # Discord scraping & DMs
│   ├── analysis_service.py      # Message analysis & sentiment
│   ├── suggestions_service.py  # Generate Suggestions array
│   └── summary_service.py      # Summaries & classification
└── discord_bot/
    ├── bot.py             # Discord bot instance (simple client)
    └── commands.py        # Bot command handlers
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Configure environment variables in `.env`:**
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
OPENAI_API_KEY=your_openai_api_key_here
DASHBOARD_BASE_URL=https://yourapp.com/dashboard
```

## Running

Start the FastAPI server - the Discord bot will start automatically:

```bash
uvicorn app.main:app --reload
```

The bot starts in a separate thread when the FastAPI server starts. If `DISCORD_BOT_TOKEN` is not set, the bot will be skipped with a warning.

## Usage

### Discord Bot Commands

In Discord, use the following command:

```
!start_discussion How should we change the room selection process?
```

The bot will:
1. Create a new question via the API
2. Scrape relevant Discord chat history
3. Reply with an embed containing the dashboard URL

### API Endpoints

- `POST /api/questions` - Create a new discussion
  - Body: `{"question": "How should we change..."}`
  - Response: `{"question_id": "uuid", "dashboard_url": "..."}`

- `GET /api/dashboard/{question_id}` - Get dashboard data
  - Returns: Array of `Suggestion` objects (see TypeScript type below)

- `WS /ws/{question_id}` - WebSocket for live updates
  - Streams: New suggestions as they're generated from messages

### Workflow

1. User posts `!start_discussion` command in Discord
2. Bot calls `POST /api/questions` with the question
3. Backend creates question state and scrapes Discord history
4. Messages are analyzed and clustered into themes
5. Suggestions are generated with pros/cons and people opinions
6. Dashboard displays live updates via WebSocket
7. Bot sends DMs to introverted users for their views


## Development Status

All function signatures and data types are implemented. The following services need implementation:
- `discord_service.py` - Discord API integration for scraping and DMs
- `analysis_service.py` - AI/ML for sentiment analysis and topic extraction
- `summary_service.py` - 2-word summary generation and classification
- `suggestions_service.py` - Generating the Suggestions array from messages

