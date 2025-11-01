"""
Embedding cache service for persisting and retrieving message embeddings
"""
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from openai import OpenAI
from app.config import settings
import threading

EMBEDDING_CACHE_DIR = Path("data")
EMBEDDING_CACHE_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDING_CACHE_FILE = EMBEDDING_CACHE_DIR / "embeddings_cache.json"
EMBEDDING_MODEL = "text-embedding-3-small"

# Thread lock for safe concurrent access
_cache_lock = threading.Lock()

# In-memory cache for quick access (loaded once, updated in memory, saved periodically)
_embeddings_cache: Optional[Dict[str, Dict]] = None


def _get_message_hash(message: str) -> str:
    """Generate hash for message content"""
    return hashlib.sha256(message.encode('utf-8')).hexdigest()


def _load_embeddings_cache() -> Dict[str, Dict]:
    """Load embeddings cache from disk"""
    if not EMBEDDING_CACHE_FILE.exists():
        return {}
    
    try:
        with open(EMBEDDING_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            # Validate format and filter by model
            filtered_cache = {}
            for msg_hash, entry in cache_data.items():
                if isinstance(entry, dict) and entry.get("model") == EMBEDDING_MODEL:
                    filtered_cache[msg_hash] = entry
            return filtered_cache
    except Exception as e:
        print(f"Error loading embeddings cache: {e}")
        return {}


def _save_embeddings_cache() -> None:
    """Save embeddings cache to disk"""
    global _embeddings_cache
    if _embeddings_cache is None:
        return
    
    try:
        with open(EMBEDDING_CACHE_FILE, 'w') as f:
            json.dump(_embeddings_cache, f, indent=2)
    except Exception as e:
        print(f"Error saving embeddings cache: {e}")


def get_cached_embedding(message: str) -> Optional[np.ndarray]:
    """Get cached embedding for a message if it exists"""
    global _embeddings_cache
    
    message_hash = _get_message_hash(message)
    
    with _cache_lock:
        # Load cache if not already loaded
        if _embeddings_cache is None:
            _embeddings_cache = _load_embeddings_cache()
        
        if message_hash in _embeddings_cache:
            entry = _embeddings_cache[message_hash]
            # Verify it's the same message and model
            if entry.get("message") == message and entry.get("model") == EMBEDDING_MODEL:
                return np.array(entry["embedding"])
    
    return None


def cache_embedding(message: str, embedding: np.ndarray) -> None:
    """Cache an embedding for a message"""
    global _embeddings_cache
    
    message_hash = _get_message_hash(message)
    
    with _cache_lock:
        # Load cache if not already loaded
        if _embeddings_cache is None:
            _embeddings_cache = _load_embeddings_cache()
        
        # Add to in-memory cache
        _embeddings_cache[message_hash] = {
            "message": message,
            "model": EMBEDDING_MODEL,
            "embedding": embedding.tolist(),
        }
        
        # Save to disk (atomic write)
        _save_embeddings_cache()


async def get_embedding(message: str, use_cache: bool = True) -> np.ndarray:
    """Get embedding for a message, using cache if available"""
    # Try cache first
    if use_cache:
        cached = get_cached_embedding(message)
        if cached is not None:
            return cached
    
    # Generate new embedding
    client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    if not client:
        raise ValueError("OpenAI API key not configured")
    
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=message
    )
    embedding = np.array(response.data[0].embedding)
    
    # Cache it
    if use_cache:
        cache_embedding(message, embedding)
    
    return embedding


async def get_embeddings_batch(messages: List[str], use_cache: bool = True) -> np.ndarray:
    """Get embeddings for multiple messages, using cache where possible"""
    embeddings = []
    messages_to_fetch = []
    indices_to_fetch = []
    
    # Check cache for each message
    for idx, msg in enumerate(messages):
        if use_cache:
            cached = get_cached_embedding(msg)
            if cached is not None:
                embeddings.append((idx, cached))
                continue
        
        messages_to_fetch.append(msg)
        indices_to_fetch.append(idx)
    
    # Fetch missing embeddings in batch
    if messages_to_fetch:
        client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        if not client:
            raise ValueError("OpenAI API key not configured")
        
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=messages_to_fetch
        )
        
        # Cache and add to results
        for i, item in enumerate(response.data):
            embedding = np.array(item.embedding)
            msg_idx = indices_to_fetch[i]
            msg = messages_to_fetch[i]
            
            if use_cache:
                cache_embedding(msg, embedding)
            
            embeddings.append((msg_idx, embedding))
    
    # Sort by original index and return as array
    embeddings.sort(key=lambda x: x[0])
    return np.array([emb for _, emb in embeddings])

