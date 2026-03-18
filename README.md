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

## Installation

### Prerequisites

| Requirement | Version | Why |
|-------------|---------|-----|
| Python | 3.10+ | Scripts and utilities |
| Docker | 20.10+ | Runs Qdrant container |
| Docker Compose | v2+ | Service orchestration |
| Git | Any | Clone this repo |

---

### macOS (Apple Silicon & Intel)

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Docker Desktop
brew install --cask docker
# Open Docker Desktop from Applications and complete setup

# 3. Install Python (if not installed)
brew install python@3.12

# 4. Install Ollama
brew install ollama
ollama serve &                    # Start Ollama in background
ollama pull nomic-embed-text      # Download embedding model

# 5. Clone and set up this repo
git clone https://github.com/NathanMaine/rah-qdrant-integration.git
cd rah-qdrant-integration
pip3 install -r requirements.txt
cp .env.example .env

# 6. Start Qdrant
docker compose up -d

# 7. Verify everything works
python3 examples/basic_usage.py
```

---

### Linux (Ubuntu/Debian)

```bash
# 1. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
newgrp docker

# 2. Install Python
sudo apt install -y python3 python3-pip python3-venv

# 3. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &                    # Start Ollama in background
ollama pull nomic-embed-text      # Download embedding model

# 4. Clone and set up this repo
git clone https://github.com/NathanMaine/rah-qdrant-integration.git
cd rah-qdrant-integration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 5. Start Qdrant
docker compose up -d

# 6. Verify everything works
python3 examples/basic_usage.py
```

**Linux ARM64 (NVIDIA DGX Spark, Jetson, Raspberry Pi):**
Same steps as above. Both Qdrant and Ollama have native ARM64 Docker images — no changes needed.

---

### Windows

```powershell
# 1. Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop/
# Enable WSL 2 backend during installation
# Restart your computer after installation

# 2. Install Python
# Download from https://www.python.org/downloads/
# IMPORTANT: Check "Add Python to PATH" during installation

# 3. Install Ollama
# Download from https://ollama.ai/download/windows
# After installation, open a terminal:
ollama serve                          # Start Ollama (leave this terminal open)
# In a NEW terminal:
ollama pull nomic-embed-text          # Download embedding model

# 4. Clone and set up this repo (in a new terminal)
git clone https://github.com/NathanMaine/rah-qdrant-integration.git
cd rah-qdrant-integration
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 5. Start Qdrant
docker compose up -d

# 6. Verify everything works
python examples/basic_usage.py
```

**Windows Notes:**
- Docker Desktop must be running before `docker compose up`
- If you get permission errors, run your terminal as Administrator
- Use `python` instead of `python3` on Windows
- WSL 2 is recommended for best Docker performance

---

### Verify Installation

After setup on any platform, verify all services are running:

```bash
# Check Qdrant is reachable
curl http://localhost:6333/collections

# Check Ollama is running
curl http://localhost:11434/api/tags

# Run the example
python3 examples/basic_usage.py
```

Expected output:
```
1. Ingesting sample content...
   Ingested 2 chunks

2. Searching for 'model evaluation metrics'...
   [0.8234] Example Expert: Machine learning models require...

3. Searching with creator filter...
   [0.8234] Example Expert: Machine learning models require...

4. Collection stats: 2 points, status: green
```

---

## Usage

### Ingest Content

```bash
# Ingest a directory of text files
python3 qdrant_ingest.py --input /path/to/documents --creator "Source Name"

# Ingest with custom chunk size
python3 qdrant_ingest.py --input /path/to/documents --creator "Source Name" --chunk-size 400 --overlap 50
```

### Search

```bash
# CLI search
python3 qdrant_search.py "your search query"

# Filter by creator
python3 qdrant_search.py "your search query" --creator "Source Name"

# More results
python3 qdrant_search.py "your search query" --limit 20

# Collection stats
python3 qdrant_search.py --stats
```

### Python API

```python
from qdrant_utils import search_vectors, upsert_chunks, chunk_text

# Search
results = search_vectors("how does attention work?", limit=10)
for r in results:
    print(f"{r['score']:.3f} — {r['creator']}: {r['text'][:100]}")

# Search with creator filter
results = search_vectors("how does attention work?", creator="Specific Expert")

# Ingest text programmatically
chunks = chunk_text("Your long document text here...", chunk_size=400, overlap=50)
upsert_chunks(chunks, creator="My Expert", title="Document Title")
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
