.PHONY: install start stop search ingest test status

# Quick start — install everything and run the example
install:
	pip3 install -r requirements.txt
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d
	@echo ""
	@echo "✓ Qdrant running on http://localhost:6333"
	@echo "✓ Run 'make test' to verify"

# Start Qdrant
start:
	docker compose up -d

# Stop Qdrant
stop:
	docker compose down

# Run the example to verify everything works
test:
	python3 examples/basic_usage.py

# Search (usage: make search q="your query")
search:
	python3 qdrant_search.py "$(q)"

# Ingest a directory (usage: make ingest dir=/path/to/files creator="Name")
ingest:
	python3 qdrant_ingest.py --input "$(dir)" --creator "$(creator)"

# Show collection stats
status:
	@python3 -c "from qdrant_utils import get_collection_stats; s=get_collection_stats(); print(f'Points: {s[\"points\"]} | Status: {s[\"status\"]}')"
