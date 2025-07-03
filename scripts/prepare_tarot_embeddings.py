"""Generate embeddings for tarot cards and upload to Qdrant.

Usage:
    python scripts/prepare_tarot_embeddings.py

Environment variables expected:
    OPENAI_API_KEY           - OpenAI key for embeddings
    QDRANT_HOST              - Qdrant host (default: localhost)
    QDRANT_PORT              - Qdrant port (default: 6333)
    QDRANT_COLLECTION        - Collection name (default: tarot_cards)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY not set"

client = OpenAI(api_key=OPENAI_API_KEY)

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
collection_name = os.getenv("QDRANT_COLLECTION", "tarot_cards")

qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

# Load tarot data
with DATA_PATH.open("r", encoding="utf-8") as fp:
    cards = json.load(fp)

# Ensure collection exists
if collection_name not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=3072, distance=rest.Distance.COSINE),  # text-embedding-3-large dims
    )

# Prepare embeddings and payloads
texts = [card["meaning"] for card in cards]
emb_res = client.embeddings.create(model="text-embedding-3-large", input=texts)

points = []
for card, emb in zip(cards, emb_res.data, strict=True):
    points.append(
        rest.PointStruct(
            id=card["id"],
            vector=emb.embedding,
            payload=card,
        )
    )

# Upsert
qdrant.upsert(collection_name=collection_name, wait=True, points=points)
print(f"Upserted {len(points)} cards to Qdrant collection '{collection_name}'.")
