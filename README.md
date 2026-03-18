# RA-H + Qdrant Integration

A community add-on that brings [Qdrant](https://qdrant.tech/) vector search to [RA-H OS](https://github.com/bradwmorris/ra-h_os) by Bradley Morris.

## What This Is

This project extends RA-H OS with a Qdrant vector database backend, enabling high-performance semantic search alongside the existing SQLite knowledge graph. It was built as a practical solution for environments where `sqlite-vec` doesn't work reliably — specifically ARM64 devices (like the NVIDIA DGX Spark) and NFS-mounted storage.

**This is not a fork or replacement.** RA-H OS remains the core platform. This integration runs alongside it, adding vector search capabilities while preserving the full node/edge/dimension graph that makes RA-H OS powerful.

## Credits

- **[RA-H OS](https://github.com/bradwmorris/ra-h_os)** by [Bradley Morris](https://github.com/bradwmorris) — the knowledge graph platform this integration extends. All graph architecture, node/edge schema, skills system, and core design are Bradley's work.
- **[Qdrant](https://qdrant.tech/)** — open-source vector database used for semantic search.
- **Integration layer** by [Nathan Maine](https://github.com/NathanMaine) — the Qdrant adapter, Docker configuration, and search utilities in this repo.

## Why Qdrant?

RA-H OS uses SQLite for its knowledge graph, which is excellent for graph queries and relationship traversal. However, for large-scale semantic search (50K+ chunks), a dedicated vector database provides:

- **ARM64 native support** — runs on NVIDIA DGX Spark, Raspberry Pi, Apple Silicon without compatibility issues
- **Docker-based** — portable across any environment, no native compilation needed
- **NFS/network storage compatible** — works reliably over mounted network drives
- **Horizontal scaling** — handles millions of vectors without degradation
- **Payload filtering** — filter search results by metadata (creator, source, tags) at query time

## Architecture

```
┌─────────────────────────────────┐
│         RA-H OS (existing)      │
│  SQLite: nodes, edges, dims     │
│  Skills: Traverse, Connect      │
└──────────────┬──────────────────┘
               │ runs alongside
┌──────────────┴──────────────────┐
│     Qdrant Integration (this)   │
│  Vector search for chunks       │
│  Payload filtering by creator   │
│  Embedding via Ollama           │
└─────────────────────────────────┘
```

RA-H OS owns the graph. Qdrant owns the vectors. Both use the same source content.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- [Ollama](https://ollama.ai/) running with an embedding model
- An existing RA-H OS installation (or standalone)

### 1. Start Qdrant

```bash
docker compose up -d
```

This starts Qdrant on port 6333 with persistent storage.

### 2. Configure

Copy the example environment file and adjust:

```bash
cp .env.example .env
```

```env
QDRANT_URL=http://localhost:6333
OLLAMA_URL=http://localhost:11434
COLLECTION_NAME=rah_vectors
EMBED_MODEL=nomic-embed-text
```

### 3. Ingest Content

```bash
# Ingest a directory of text files
python qdrant_ingest.py --input /path/to/documents --creator "Source Name"

# Ingest with custom chunk size
python qdrant_ingest.py --input /path/to/documents --creator "Source Name" --chunk-size 400 --overlap 50
```

### 4. Search

```bash
# CLI search
python qdrant_search.py "your search query"

# Filter by creator
python qdrant_search.py "your search query" --creator "Source Name"
```

### 5. Python API

```python
from qdrant_client import QdrantClient
from qdrant_utils import embed_text, search_vectors

# Search
results = search_vectors("how does attention work?", limit=10)
for r in results:
    print(f"{r['score']:.3f} — {r['creator']}: {r['text'][:100]}")

# Search with creator filter
results = search_vectors("how does attention work?", creator="Specific Expert")
```

## File Structure

```
rah-qdrant-integration/
├── README.md
├── docker-compose.yml       # Qdrant service definition
├── .env.example             # Configuration template
├── qdrant_utils.py          # Core utilities (embed, search, upsert)
├── qdrant_ingest.py         # CLI tool to ingest text files
├── qdrant_search.py         # CLI search tool
├── requirements.txt         # Python dependencies
└── examples/
    └── basic_usage.py       # Example integration script
```

## Docker Compose

The included `docker-compose.yml` runs Qdrant with persistent storage:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  qdrant_data:
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server for embeddings |
| `COLLECTION_NAME` | `rah_vectors` | Qdrant collection name |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model (768 dimensions) |
| `CHUNK_SIZE` | `400` | Words per chunk |
| `CHUNK_OVERLAP` | `50` | Word overlap between chunks |

## Embedding Models

This integration uses [Ollama](https://ollama.ai/) for local embedding generation. Install an embedding model:

```bash
ollama pull nomic-embed-text
```

Any Ollama-compatible embedding model works. Adjust `EMBED_MODEL` in your `.env` file.

## Compatibility

| Platform | Status |
|----------|--------|
| Linux x86_64 | Tested |
| Linux ARM64 (DGX Spark) | Tested |
| macOS (Apple Silicon) | Tested |
| Windows (Docker Desktop) | Should work (untested) |

## Integration with RA-H OS

This runs **alongside** RA-H OS, not inside it. To connect both systems:

1. When content is added to RA-H OS nodes, also ingest it into Qdrant
2. Use RA-H OS for graph traversal (relationships, dimensions, skills)
3. Use Qdrant for semantic search (find relevant content by meaning)

The two systems complement each other — graphs for structure, vectors for similarity.

## License

MIT — same as RA-H OS.

## Links

- [RA-H OS](https://github.com/bradwmorris/ra-h_os) — the platform this extends
- [Bradley Morris](https://www.bradwmorris.com/) — RA-H OS creator
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama](https://ollama.ai/) — local embedding model server
