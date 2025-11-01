# BaselHack25 Consensus Builder Backend

Discord bot backend for building consensus through AI analysis of discussions.

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration settings
├── state.py                # In-memory state management
├── api/
│   ├── schemas.py          # Pydantic models (matches TypeScript types)
│   └── routes/
│       ├── questions.py    # POST /api/questions
│       ├── dashboard.py    # GET /api/dashboard/:question_id
│       └── websocket.py   # WS /ws/:question_id
├── services/
│   ├── discord_service.py  # Discord scraping & DMs
│   ├── analysis_service.py     # Message analysis
│   ├── suggestions_service.py  # Generate Suggestions
│   └── summary_service.py      # Summaries & classification
└── discord_bot/
    ├── bot.py             # Discord bot instance
    └── commands.py        # Bot command handlers
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Fill in your Discord bot token and API keys in `.env`

## Running

### API Server
```bash
uvicorn app.main:app --reload
```

### Discord Bot
```bash
python -m app.discord_bot.bot
```

## API Endpoints

- `POST /api/questions` - Create a new discussion
- `GET /api/dashboard/{question_id}` - Get dashboard data (returns Suggestions array)
- `WS /ws/{question_id}` - WebSocket for live updates

## TypeScript Compatibility

The API responses match the TypeScript `Suggestions` type:
```typescript
type Suggestions = {
  title: string;
  size: number; // 0 - 1
  pros: string[];
  contra: string[];
  peopleOpinions: {
    name: string;
    profilePicUrl: string;
    message: string;
    classification: "sophisticated" | "simple" | "neutral";
  }[];
}[];
```

