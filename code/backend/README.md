# BaselHack25 Consensus Builder Backend

FastAPI backend with Discord bot integration for building consensus through AI analysis of discussions. Part of the [BaselHack 2025 Collective Intelligence Challenge](https://www.baselhack.ch/challenges/collective-intelligence-building-consensus-through-ai).

## Overview

- Real-time semantic clustering using Agglomerative Clustering
- GPT-based embeddings (OpenAI) with intelligent caching
- Centroid-based two-word label generation
- REST API and WebSocket for dashboard integration
- PDF report generation with WeasyPrint
- In-memory state with JSON persistence

## AI Methodology

Messages are embedded into high-dimensional semantic space. Agglomerative Clustering groups them into coherent perspectives. The **centroid** (geometric mean of embeddings) represents each cluster's semantic center. Two-word labels are generated from messages nearest to this centroid point, ensuring labels reflect the consensus position.

**Key Features:**
- Embedding cache with content-based hashing
- L2 normalization for consistent similarity calculations
- Periodic clustering maintains quality in real-time
- Configurable consensus detection thresholds

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```env
   DISCORD_BOT_TOKEN=your_token
   DISCORD_GUILD_ID=your_guild_id
   OPENAI_API_KEY=your_key
   DASHBOARD_BASE_URL=http://localhost:3000/dashboard
   CORS_ORIGINS=["http://localhost:3000"]
   ```

3. **Run:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Discord bot starts automatically.

## API Endpoints

- `POST /api/questions` - Create discussion (returns `question_id`, `dashboard_url`)
- `GET /api/dashboard/{question_id}` - Get cluster data and consensus scores
- `GET /api/messages` - Get all cached messages
- `GET /api/report/{question_id}` - Generate PDF report
- `WS /ws/{question_id}` - Live updates stream
- `GET /docs` - Interactive API documentation

## Workflow

1. Create question via API
2. System analyzes relevant Discord history using semantic similarity
3. New messages are assigned to clusters in real-time
4. Periodic clustering maintains quality using Agglomerative Clustering
5. Two-word labels generated from messages nearest to cluster centroids
6. Dashboard receives live updates via WebSocket

## State & Configuration

**State Management:** In-memory with JSON persistence (no database). Cache files in `data/`:
- `all_discord_messages.json` - Global message cache
- `active_question.json` - Current question state
- `embeddings_cache.json` - Embedding cache

**Configuration:** Environment variables control clustering thresholds, similarity settings, and Discord integration. See `.env` example above.

## Tech Stack

- Python 3.12 + FastAPI
- OpenAI API (embeddings: `text-embedding-3-small`, LLM: `gpt-4o-mini`)
- scikit-learn (Agglomerative Clustering)
- discord.py, WeasyPrint, Uvicorn
