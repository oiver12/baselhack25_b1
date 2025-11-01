"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import questions, dashboard, websocket
from app.config import settings

app = FastAPI(title="BaselHack25 Consensus Builder API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "BaselHack25 Consensus Builder API"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

