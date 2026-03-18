#!/usr/bin/env python3
"""
Ingest text files into Qdrant for RA-H OS vector search.

Usage:
    python qdrant_ingest.py --input /path/to/files --creator "Expert Name"
    python qdrant_ingest.py --input /path/to/files --creator "Expert Name" --chunk-size 300
"""

import argparse
import os
import sys
from pathlib import Path

from qdrant_utils import chunk_text, upsert_chunks, get_collection_stats


def ingest_directory(input_dir: str, creator: str, chunk_size: int = 400, overlap: int = 50):
    """Ingest all .txt files from a directory into Qdrant."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    files = sorted(input_path.glob("*.txt"))
    if not files:
        print(f"No .txt files found in {input_dir}")
        sys.exit(1)

    print(f"Ingesting {len(files)} files for creator: {creator}")
    total_chunks = 0

    for i, filepath in enumerate(files, 1):
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        if len(text.strip()) < 100:
            continue

        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        upsert_chunks(chunks, creator=creator, title=filepath.stem, source=str(filepath))
        total_chunks += len(chunks)

        if i % 10 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] {total_chunks} chunks so far...")

    stats = get_collection_stats()
    print(f"\nDone: {total_chunks} chunks ingested for {creator}")
    print(f"Collection total: {stats['points']} points")


def main():
    parser = argparse.ArgumentParser(description="Ingest text files into Qdrant")
    parser.add_argument("--input", required=True, help="Directory containing .txt files")
    parser.add_argument("--creator", required=True, help="Creator/expert name for metadata")
    parser.add_argument("--chunk-size", type=int, default=400, help="Words per chunk (default: 400)")
    parser.add_argument("--overlap", type=int, default=50, help="Word overlap (default: 50)")
    args = parser.parse_args()

    ingest_directory(args.input, args.creator, args.chunk_size, args.overlap)


if __name__ == "__main__":
    main()
