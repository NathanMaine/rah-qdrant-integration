#!/usr/bin/env python3
"""
Basic usage example for the RA-H + Qdrant integration.

Demonstrates:
1. Ingesting text content with creator attribution
2. Searching with semantic similarity
3. Filtering results by creator
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qdrant_utils import chunk_text, upsert_chunks, search_vectors, get_collection_stats

# --- Example: Ingest some content ---
sample_text = """
Machine learning models require careful evaluation to ensure they generalize
well to unseen data. Common metrics include accuracy, precision, recall, and
F1 score. For regression tasks, mean squared error and R-squared are standard.
Cross-validation helps estimate model performance by training on different
subsets of the data and averaging the results.
"""

print("1. Ingesting sample content...")
chunks = chunk_text(sample_text, chunk_size=50, overlap=10)
upsert_chunks(chunks, creator="Example Expert", title="ML Evaluation Basics")
print(f"   Ingested {len(chunks)} chunks\n")

# --- Example: Search ---
print("2. Searching for 'model evaluation metrics'...")
results = search_vectors("model evaluation metrics", limit=3)
for r in results:
    print(f"   [{r['score']}] {r['creator']}: {r['text'][:100]}...")
print()

# --- Example: Filter by creator ---
print("3. Searching with creator filter...")
results = search_vectors("evaluation", limit=3, creator="Example Expert")
for r in results:
    print(f"   [{r['score']}] {r['creator']}: {r['text'][:100]}...")
print()

# --- Example: Collection stats ---
stats = get_collection_stats()
print(f"4. Collection stats: {stats['points']} points, status: {stats['status']}")
