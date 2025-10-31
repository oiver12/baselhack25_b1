# Basel Hack 25 Backend - Collective Intelligence Discord Bot

Backend API for the Collective Intelligence Discord Bot that helps build consensus through AI analysis.

## Features

- Create discussion sessions from Discord questions
- Real-time analysis of Discord messages
- Generate Suggestions with pros/cons and participant opinions
- Live WebSocket updates for dashboard
- Discord bot integration with `!start_discussion` command

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

3. Set up Discord bot:
   - Create a Discord bot at https://discord.com/developers/applications
   - Get your bot token and add it to `.env`
   - Enable message content intent in Discord Developer Portal
   - Invite bot to your server with required permissions

4. Run the server:
```bash
python -m app.main
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /api/questions
Create a new discussion/question session.

**Request:**
```json
{
  "question": "How should we change the room selection process?"
}
```

**Response:**
```json
{
  "question_id": "8f4f92a1-d58a-4b10-a871-2c23b050c5ae",
  "dashboard_url": "http://localhost:3000/dashboard/8f4f92a1-d58a-4b10-a871-2c23b050c5ae"
}
```

### GET /api/dashboard/{question_id}
Get dashboard data (Suggestions array).

**Response:**
```json
[
  {
    "title": "Voting-based selection",
    "size": 0.65,
    "pros": ["Fair", "Democratic"],
    "contra": ["Time consuming"],
    "people_opinions": [
      {
        "name": "Alice",
        "profile_pic_url": "https://...",
        "message": "I think we should vote...",
        "classification": "sophisticated"
      }
    ]
  }
]
```

### GET /api/dashboard/{question_id}/bubbles
Get live bubbles (2-word summaries).

### WebSocket: /ws/{question_id}
Connect for real-time updates.

**Messages:**
- `initial`: Initial data when connecting
- `suggestions_updated`: Suggestions have been updated
- `new_bubble`: New bubble (2-word summary) added

## Discord Bot Commands

### !start_discussion <question>
Start a new discussion session. The bot will:
1. Create a question session via the API
2. Post a message with the dashboard link
3. Begin analyzing relevant Discord messages

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
├── state.py             # In-memory state management
├── api/
│   ├── schemas.py       # Pydantic models (matches TypeScript)
│   └── routes/          # API endpoints
├── services/            # Business logic
│   ├── discord_service.py
│   ├── analysis_service.py
│   ├── suggestions_service.py
│   └── summary_service.py
└── discord_bot/         # Discord bot implementation
```

## Development

The backend uses in-memory state (no database). All data is stored in `state_manager` which persists during the server's lifetime.

For production, consider adding:
- Database persistence
- Redis for distributed state
- Better AI analysis (OpenAI, Anthropic)
- Message queue for background processing

## License

MIT

