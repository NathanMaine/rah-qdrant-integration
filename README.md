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

## Troubleshooting

### All Platforms

**"Connection refused" when accessing Qdrant (port 6333)**
```bash
# Check if Docker is running
docker ps

# If Qdrant container isn't listed, start it
docker compose up -d

# Check Qdrant logs for errors
docker logs rah-qdrant
```

**"Failed to generate embedding" / Ollama connection errors**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve &

# Verify the embedding model is downloaded
ollama list
# If nomic-embed-text is not listed:
ollama pull nomic-embed-text
```

**"No results found" after ingesting content**
```bash
# Verify chunks were actually ingested
python3 qdrant_search.py --stats
# Should show points > 0

# If points is 0, the ingestion failed silently. Check:
# 1. Are your files .txt format? The ingest script reads *.txt only
# 2. Are files > 100 characters? Very short files are skipped
# 3. Is Ollama running? Embedding generation requires it
```

**Qdrant runs out of memory on large datasets**
```bash
# Check Qdrant memory usage
docker stats rah-qdrant

# If memory is high, restart with memory limits in docker-compose.yml:
# services:
#   qdrant:
#     deploy:
#       resources:
#         limits:
#           memory: 4G
```

---

### macOS

**Docker Desktop not starting / "Cannot connect to Docker daemon"**
```bash
# Open Docker Desktop from Applications manually
open -a Docker

# Wait 30 seconds for it to initialize, then verify
docker ps
```

**Apple Silicon (M1/M2/M3): "exec format error" on container start**
This means a container image doesn't have an ARM64 build. Both Qdrant and Ollama have ARM64 images, so this shouldn't happen. If it does:
```bash
# Force the correct platform
docker compose down
DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose up -d
```

**"pip3: command not found" after installing Python via Homebrew**
```bash
# Homebrew installs Python with a versioned name
python3.12 -m pip install -r requirements.txt
# Or create an alias
echo 'alias pip3="python3 -m pip"' >> ~/.zshrc
source ~/.zshrc
```

**Port 5000 conflict with AirPlay Receiver**
Qdrant uses port 6333, not 5000, so this shouldn't affect the integration. But if you're running other services:
- System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off

**Ollama "address already in use" on port 11434**
```bash
# Another Ollama instance is running. Kill it first
pkill ollama
ollama serve &
```

---

### Linux (Ubuntu/Debian)

**"permission denied" when running Docker commands**
```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply immediately (or log out and back in)
newgrp docker

# Verify
docker ps
```

**"docker compose" command not found (older Docker versions)**
```bash
# On older systems, it's a separate package
sudo apt install docker-compose-v2

# Or use the hyphenated version
docker-compose up -d
```

**Ollama fails to start — "NVIDIA GPU not found"**
Ollama works without a GPU (CPU-only mode). If you see GPU warnings but want to proceed:
```bash
# Ollama falls back to CPU automatically
# The warning is informational, not an error
# Embedding generation is slower on CPU but still works

# If you have an NVIDIA GPU and want to use it:
# Install the NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Linux ARM64 (DGX Spark, Jetson): "exec format error"**
```bash
# Ensure you're pulling ARM64 images (should be automatic)
docker pull --platform linux/arm64 qdrant/qdrant:latest

# Verify your architecture
uname -m
# Should output: aarch64
```

**Firewall blocking port 6333**
```bash
# If using UFW
sudo ufw allow 6333/tcp
sudo ufw allow 11434/tcp

# If using iptables
sudo iptables -A INPUT -p tcp --dport 6333 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
```

**Python venv issues — "ensurepip is not available"**
```bash
sudo apt install python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
```

---

### Windows

**Docker Desktop won't start — "WSL 2 is not installed"**
```powershell
# Open PowerShell as Administrator
wsl --install

# Restart your computer
# Then open Docker Desktop again
```

**Docker Desktop — "WSL 2 distro terminated unexpectedly"**
```powershell
# Reset WSL
wsl --shutdown
# Wait 10 seconds, then restart Docker Desktop
```

**Docker Desktop — very slow or high memory usage**
```
1. Open Docker Desktop → Settings → Resources
2. Set Memory limit to 4 GB (default may be too high)
3. Set CPU limit to 4 (adjust based on your system)
4. Apply & Restart
```

Alternatively, create/edit `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=4GB
processors=4
swap=2GB
```
Then restart WSL: `wsl --shutdown`

**"python" command not found**
```powershell
# Python may not be on PATH
# Option 1: Reinstall Python and check "Add Python to PATH"

# Option 2: Use the Windows Store version
winget install Python.Python.3.12

# Option 3: Use the full path
& "C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe" --version
```

**"pip" command not found**
```powershell
python -m pip install -r requirements.txt
```

**"docker compose" not recognized**
```powershell
# On Windows, Docker Compose v2 is built into Docker Desktop
# Make sure Docker Desktop is running first

# If still not working, try the older syntax:
docker-compose up -d
```

**Qdrant container exits immediately on Windows**
```powershell
# Check the logs
docker logs rah-qdrant

# Common cause: Windows Defender blocking the container
# Add an exclusion for Docker in Windows Security:
# Settings → Windows Security → Virus & threat protection → Manage settings
# → Exclusions → Add exclusion → Folder → C:\ProgramData\DockerDesktop
```

**"curl" not available in PowerShell**
```powershell
# Use Invoke-WebRequest instead
Invoke-WebRequest -Uri http://localhost:6333/collections | Select-Object -Expand Content

# Or install curl via winget
winget install curl.curl
```

**Permission errors when creating files/volumes**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → Run as Administrator

# Or adjust folder permissions
icacls . /grant Users:F /T
```

**Ollama won't start on Windows — "port 11434 already in use"**
```powershell
# Find what's using the port
netstat -ano | findstr :11434

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F

# Restart Ollama
ollama serve
```

---

### Docker-Specific Issues (All Platforms)

**Qdrant data lost after container restart**
The `docker-compose.yml` uses a named volume (`qdrant_data`) for persistence. If you ran Qdrant without the compose file, data may be in an anonymous volume:
```bash
# List volumes
docker volume ls

# If using the compose file, data persists in qdrant_data
# To backup:
docker run --rm -v qdrant_data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz /data
```

**Container won't start — "port already in use"**
```bash
# Find what's using port 6333
lsof -ti:6333    # macOS/Linux
netstat -ano | findstr :6333  # Windows

# Kill the process or change the port in docker-compose.yml:
# ports:
#   - "6334:6333"   # Map to different host port
# Then update QDRANT_URL in .env to http://localhost:6334
```

**"no matching manifest for linux/arm64" (ARM64 systems)**
```bash
# Force pull the ARM64 image
docker pull --platform linux/arm64 qdrant/qdrant:latest

# If still failing, use a specific version known to support ARM64
# In docker-compose.yml, change:
#   image: qdrant/qdrant:v1.12.0
```

**Container running but API returns errors**
```bash
# Check container health
docker inspect rah-qdrant | grep -A 5 "Health"

# View real-time logs
docker logs -f rah-qdrant

# Restart the container
docker compose restart
```

## Integration with RA-H OS

This runs **alongside** RA-H OS, not inside it. To connect both systems:

1. When content is added to RA-H OS nodes, also ingest it into Qdrant
2. Use RA-H OS for graph traversal (relationships, dimensions, skills)
3. Use Qdrant for semantic search (find relevant content by meaning)

The two systems complement each other — graphs for structure, vectors for similarity.

## FAQ

**Q: Do I need a GPU?**
No. Ollama runs embedding models on CPU. It's slower but works fine. A GPU speeds up embedding generation but is not required.

**Q: How much disk space does Qdrant use?**
Roughly 1-2 GB per 100,000 chunks. A typical setup with 10,000 chunks uses under 200 MB.

**Q: Can I use a different embedding model?**
Yes. Any model available through Ollama works. Change `EMBED_MODEL` in `.env`. Note: if you switch models after ingesting data, you need to re-ingest everything — embeddings from different models are not compatible.

**Q: Can I run Qdrant on a remote server?**
Yes. Change `QDRANT_URL` in `.env` to point to the remote server (e.g., `http://192.168.1.100:6333`). Make sure port 6333 is accessible.

**Q: How do I backup my data?**
```bash
# Create a Qdrant snapshot
curl -X POST http://localhost:6333/collections/rah_vectors/snapshots

# List snapshots
curl http://localhost:6333/collections/rah_vectors/snapshots

# Download a snapshot
curl http://localhost:6333/collections/rah_vectors/snapshots/<snapshot_name> -o backup.snapshot
```

**Q: Can I run this without RA-H OS?**
Yes. This integration is self-contained. Qdrant + Ollama + these scripts work independently. RA-H OS adds the knowledge graph layer but is not required for vector search.

## License

MIT — same as RA-H OS.

## Links

- [RA-H OS](https://github.com/bradwmorris/ra-h_os) — the platform this extends
- [Bradley Morris](https://www.bradwmorris.com/) — RA-H OS creator
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama](https://ollama.ai/) — local embedding model server
