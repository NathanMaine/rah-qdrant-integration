#!/usr/bin/env python3
"""
Search the Qdrant vector database.

Usage:
    python qdrant_search.py "your search query"
    python qdrant_search.py "your search query" --creator "Expert Name"
    python qdrant_search.py "your search query" --limit 20
"""

import argparse

from qdrant_utils import search_vectors, get_collection_stats


def main():
    parser = argparse.ArgumentParser(description="Search Qdrant vectors")
    parser.add_argument("query", help="Search query text")
    parser.add_argument("--creator", help="Filter by creator name")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--stats", action="store_true", help="Show collection stats and exit")
    args = parser.parse_args()

    if args.stats:
        stats = get_collection_stats()
        print(f"Collection: {stats['points']} points, status: {stats['status']}")
        return

    results = search_vectors(args.query, limit=args.limit, creator=args.creator)

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} results:\n")
    for r in results:
        print(f"  [{r['score']}] {r['creator']} — {r['title']}")
        print(f"  {r['text'][:200]}...")
        print()


if __name__ == "__main__":
    main()
