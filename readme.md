# BaselHack 2025 – AI Consensus Platform

**Tagline:** Collective Intelligence through Real-Time Clustering and Consensus Detection

---

## Table of Contents

- [BaselHack 2025 – AI Consensus Platform](#baselhack-2025--ai-consensus-platform)
  - [Table of Contents](#table-of-contents)
  - [Project Title and Description](#project-title-and-description)
  - [Our Product](#our-product)
  - [Key Features](#key-features)
  - [Architecture and Tech Stack](#architecture-and-tech-stack)
    - [Structure](#structure)
    - [Stack Overview](#stack-overview)
    - [AI Methodology](#ai-methodology)
  - [Setup and Installation](#setup-and-installation)
  - [Challenges and Learnings](#challenges-and-learnings)
  - [Contributors](#contributors)

---

## Project Title and Description

**AI Consensus** is our submission for **BaselHack 2025**, tackling the challenge of building **collective intelligence** in teams and communities.

We designed an AI-powered Discord bot and web dashboard that gather, cluster, and visualize opinions in real time — enabling groups to reach consensus faster and more transparently.

The system listens to user discussions, embeds their messages using GPT-based embeddings, clusters them semantically using hierarchical clustering, and detects agreement levels based on similarity metrics and participation ratios.

---

## Our Product

* **Discord Bot:** Collects messages per topic or question, embeds them using OpenAI's embedding API, and dynamically forms semantic clusters using Agglomerative Clustering.

* **Web Dashboard:** Displays clusters, consensus scores, and user participation with a live updating interface powered by WebSockets.

* **Backend:** Manages cluster updates in real time, stores embeddings with intelligent caching, maintains in-memory state with JSON persistence, and exposes a REST API for the dashboard.

---

## Key Features

* **Real-time message ingestion and clustering** — Messages are processed as they arrive with periodic cluster updates
* **Consensus detection** — Configurable thresholds for similarity and participation identify when groups reach agreement
* **Two-word summarization** — Each cluster is automatically labeled with a concise, meaningful summary
* **Live visualization** — Interactive dashboard with message distributions and cluster dynamics
* **PDF report generation** — Export comprehensive consensus reports with WeasyPrint
* **Embedding cache** — Intelligent caching system reduces API calls and improves performance
* **Scalable architecture** — Supports multiple channels and questions with in-memory state management

---

## Architecture and Tech Stack

### Structure

```
code/
├── backend/        # FastAPI backend handling embeddings, clustering, state
├── frontend/       # Next.js dashboard for visualization
└── ...
```

### Stack Overview

**Backend**

* Python 3.12 with FastAPI
* In-memory state with JSON file persistence (no external database)
* OpenAI API for embeddings and LLM services
* Agglomerative Clustering (scikit-learn) for semantic grouping
* Asyncio for concurrent processing
* WeasyPrint for PDF report generation
* Embedding cache with L2 normalization

### AI Methodology

**Semantic Clustering & Label Generation**

Our system employs a sophisticated geometric approach to consensus building. Each message is embedded into a high-dimensional semantic space using GPT-based embeddings. Through Agglomerative Clustering, messages naturally coalesce into coherent groups representing distinct perspectives.

The essence of each cluster is captured by computing the **centroid** — the geometric mean of all message embeddings within the cluster. This centroid represents the semantic center of gravity, a point in embedding space that embodies the collective meaning of all messages in the cluster.

For label generation, we identify the messages nearest to this centroid point, ensuring that our two-word summaries emerge from the most representative expressions at the cluster's semantic core. By grounding label generation in this geometric foundation, we ensure that cluster labels authentically reflect the consensus position rather than arbitrary message selections. This approach leverages the geometric properties of embedding spaces to create labels that are both mathematically principled and semantically meaningful.

**Frontend**

* Next.js 16 with React 19
* TypeScript for type safety
* Tailwind CSS for styling
* Recharts for cluster visualization
* WebSocket integration for live updates
* Biome for linting and formatting

**Dev & Deployment**

* Docker for containerization
* Python Alpine-based images for minimal footprint
* Uvicorn with async workers for production

---

## Setup and Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<user>/baselhack25_b1.git
   cd baselhack25_b1
   ```

2. **Backend setup**

   Create `.env` file in `code/backend/`:

   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token
   DISCORD_GUILD_ID=your_guild_id
   DISCORD_CHANNEL_ID=your_channel_id  # Optional
   OPENAI_API_KEY=your_openai_api_key
   DASHBOARD_BASE_URL=http://localhost:3000/dashboard
   CORS_ORIGINS=["http://localhost:3000"]
   ```

   Install dependencies:

   ```bash
   cd code/backend
   pip install -r requirements.txt
   ```

3. **Frontend setup**

   ```bash
   cd code/frontend
   bun install  # or npm install
   ```

4. **Run the application**

   **Backend:**
   ```bash
   cd code/backend
   uvicorn app.main:app --reload
   ```
   The Discord bot starts automatically when the FastAPI server starts.

   **Frontend:**
   ```bash
   cd code/frontend
   bun dev  # or npm run dev
   ```

5. **Access locally**

   * Frontend: [http://localhost:3000](http://localhost:3000)
   * Backend API: [http://localhost:8000](http://localhost:8000)
   * API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---


## Deployment

Both the frontend and backend are built and deployed independently.

Currently, everything is hosted on [Sevalla](https://sevalla.com):

- **Backend:**  
  The backend service is containerized using the provided `Dockerfile` in `code/backend/`.  
  Deployment steps:
  1. Build the Docker image:
     ```bash
     cd code/backend
     docker build -t ai-consensus-backend .
     ```
  2. Run the container, mapping necessary ports and mounting the `.env`:
     ```bash
     docker run --env-file .env -p 8000:8000 ai-consensus-backend
     ```

- **Frontend:**  
  The frontend is deployed using [Nixpacks](https://nixpacks.com/), which automatically detects the build environment and serves the app.
  Deployment steps:
  1. From `code/frontend/`, use the Nixpacks CLI or Sevalla dashboard to deploy:
     ```bash
     cd code/frontend
     nixpacks build .  # or use the Sevalla UI to trigger a build
     ```
     (On Sevalla, Nixpacks deployment is usually triggered automatically on push, no extra config required.)

  2. The frontend will be served over port 3000 by default.

**Note:**  
- Both services can be redeployed independently.
- You may point the frontend `.env` or runtime configs to the public API URL if backend runs remotely.

---

## Challenges and Learnings

* **Semantic clustering design** — Balancing cluster quality with minimal overlap required careful tuning of Agglomerative Clustering parameters and similarity thresholds

* **Real-time performance** — Implementing embedding caching with L2 normalization and intelligent batch processing was crucial for maintaining responsiveness

* **State synchronization** — Managing live data flow between Discord, backend, and dashboard required robust state management with JSON persistence for reliability

* **Concise summarization** — Generating meaningful two-word cluster labels without duplicates became an engaging prompt-engineering challenge

* **Consensus detection** — Developing configurable thresholds that accurately identify agreement while avoiding false positives required extensive testing and refinement

---

## Contributors

* [Oliver Baumgartner](https://github.com/oiver12)
* [Samel Baumgartner](https://github.com/)
* [Sven Messmer](https://github.com/Halllo5)
* [Kimi Löffel](https://github.com/MrSpoony)

