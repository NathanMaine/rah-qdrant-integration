"""
Qdrant utilities for RA-H OS integration.
Provides embedding, search, and upsert functions.

Requires:
  - Qdrant running (default: http://localhost:6333)
  - Ollama running with an embedding model (default: nomic-embed-text)
"""

import os
import sys
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION = os.getenv("COLLECTION_NAME", "rah_vectors")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
VECTOR_DIM = 768


def _check_service(url, name):
    """Verify a service is reachable. Returns True or prints helpful error."""
    try:
        requests.get(url, timeout=3)
        return True
    except requests.ConnectionError:
        print(f"\n[ERROR] Cannot connect to {name} at {url}")
        if "6333" in url:
            print(f"  Is Qdrant running? Try: docker compose up -d")
        elif "11434" in url:
            print(f"  Is Ollama running? Try: ollama serve")
        print()
        return False


def ensure_collection():
    """Create the Qdrant collection if it doesn't exist."""
    if not _check_service(QDRANT_URL, "Qdrant"):
        return False
    try:
        resp = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=5)
        if resp.status_code == 200:
            return True
        resp = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}",
            json={
                "vectors": {"size": VECTOR_DIM, "distance": "Cosine"},
            },
            timeout=10,
        )
        if resp.ok:
            print(f"Created collection '{COLLECTION}' ({VECTOR_DIM} dimensions, cosine distance)")
        return resp.ok
    except Exception as e:
        print(f"[ERROR] Failed to create collection: {e}")
        return False


def embed_text(text: str) -> list[float]:
    """Generate an embedding vector using Ollama."""
    if not _check_service(OLLAMA_URL, "Ollama"):
        sys.exit(1)
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        if resp.status_code == 404:
            print(f"\n[ERROR] Embedding model '{EMBED_MODEL}' not found in Ollama.")
            print(f"  Install it: ollama pull {EMBED_MODEL}")
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()["embedding"]
    except requests.ConnectionError:
        print(f"\n[ERROR] Lost connection to Ollama at {OLLAMA_URL}")
        print(f"  Restart it: ollama serve")
        sys.exit(1)


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def upsert_chunks(chunks: list[str], creator: str, title: str = "", source: str = ""):
    """Embed and upsert text chunks into Qdrant."""
    ensure_collection()
    points = []
    for i, chunk in enumerate(chunks):
        vector = embed_text(chunk)
        points.append({
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
                "text": chunk,
                "creator": creator,
                "title": title,
                "source": source,
                "chunk_index": i,
            },
        })
        # Batch upsert every 50 points
        if len(points) >= 50:
            _upsert_batch(points)
            points = []
    if points:
        _upsert_batch(points)


def _upsert_batch(points: list[dict]):
    """Upsert a batch of points to Qdrant."""
    requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points",
        json={"points": points},
        timeout=30,
    )


def search_vectors(query: str, limit: int = 10, creator: str = None) -> list[dict]:
    """Search Qdrant with a text query."""
    vector = embed_text(query)
    body = {
        "vector": vector,
        "limit": limit,
        "with_payload": True,
    }
    if creator:
        body["filter"] = {
            "must": [{"key": "creator", "match": {"value": creator}}]
        }
    resp = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        json=body,
        timeout=15,
    )
    resp.raise_for_status()
    results = []
    for hit in resp.json().get("result", []):
        payload = hit.get("payload", {})
        results.append({
            "score": round(hit.get("score", 0), 4),
            "creator": payload.get("creator", ""),
            "title": payload.get("title", ""),
            "text": payload.get("text", ""),
            "source": payload.get("source", ""),
        })
    return results


def get_collection_stats() -> dict:
    """Get collection statistics."""
    resp = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=5)
    if resp.ok:
        result = resp.json().get("result", {})
        return {
            "points": result.get("points_count", 0),
            "status": result.get("status", "unknown"),
        }
    return {"points": 0, "status": "unreachable"}
