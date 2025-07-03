"""RAG (Retrieval Augmented Generation) service for tarot card meanings."""
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import logging

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Distance, VectorParams
from openai import OpenAI

# Constants
# Default to Ollama collection, fallback to OpenAI collection
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "tarot_cards_ollama_nomic-embed-text")

# Ollama configuration
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() in ("true", "1", "yes")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
OLLAMA_EMBEDDING_DIM = 768  # nomic-embed-text dimension

# OpenAI configuration (fallback)
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
OPENAI_EMBEDDING_DIM = 3072

# Use appropriate dimension based on whether Ollama is enabled
EMBEDDING_DIM = OLLAMA_EMBEDDING_DIM if OLLAMA_ENABLED else OPENAI_EMBEDDING_DIM

SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score for results


class RAGService:
    """Service for RAG operations on tarot cards."""

    _instance = None
    _client = None
    _openai = None

    @classmethod
    def get_instance(cls) -> "RAGService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize RAG service with connections to Qdrant and embedding providers."""
        global OLLAMA_ENABLED, EMBEDDING_DIM
        
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # Initialize OpenAI client if needed
        if not OLLAMA_ENABLED:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set and Ollama is disabled")
            self._openai = OpenAI(api_key=openai_api_key)
        else:
            # Check Ollama availability
            try:
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(f"{OLLAMA_BASE_URL}/api/version")
                    version = response.json().get("version")
                    logging.info(f"Connected to Ollama API, version: {version}")
            except Exception as e:
                logging.error(f"Failed to connect to Ollama API at {OLLAMA_BASE_URL}: {e}")
                # Fall back to OpenAI if Ollama fails
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if openai_api_key:
                    logging.info("Falling back to OpenAI embeddings")
                    self._openai = OpenAI(api_key=openai_api_key)
                    OLLAMA_ENABLED = False
                    EMBEDDING_DIM = OPENAI_EMBEDDING_DIM
                else:
                    raise ValueError("No embedding service available: Ollama failed and OPENAI_API_KEY not set")

        # Connect to Qdrant
        try:
            self._client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            collections = self._client.get_collections()
            logging.info(f"Connected to Qdrant. Available collections: {collections}")
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant: {e}")
            self._client = None

    def create_collection_if_not_exists(self) -> bool:
        """Create tarot card collection if it doesn't exist."""
        if not self._client:
            return False

        try:
            collections = self._client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if COLLECTION_NAME not in collection_names:
                logging.info(f"Creating collection: {COLLECTION_NAME}")
                self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIM,
                        distance=Distance.COSINE,
                    ),
                )
                return True
            return True
        except Exception as e:
            logging.error(f"Failed to create collection: {e}")
            return False

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama or OpenAI API."""
        if OLLAMA_ENABLED:
            return await self.generate_ollama_embedding(text)
        else:
            return await self.generate_openai_embedding(text)
    
    async def generate_ollama_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama API."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json={"model": OLLAMA_MODEL, "prompt": text}
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
        except Exception as e:
            logging.error(f"Failed to generate Ollama embedding: {e}")
            raise

    async def generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API."""
        try:
            response = await self._openai.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=text,
                dimensions=OPENAI_EMBEDDING_DIM
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Failed to generate OpenAI embedding: {e}")
            raise

    async def query(self, text: str, limit: int = 5, 
                   filter_params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Query Qdrant for similar tarot cards based on text."""
        if not self._client:
            raise ConnectionError("Qdrant client not initialized")

        # Generate embedding for query text
        embedding = await self.generate_embedding(text)
        
        # Build filter if params provided
        search_filter = None
        if filter_params:
            conditions = []
            if "arcana" in filter_params:
                conditions.append(
                    FieldCondition(
                        key="arcana",
                        match=MatchValue(value=filter_params["arcana"])
                    )
                )
            if "orientation" in filter_params:
                conditions.append(
                    FieldCondition(
                        key="orientation",
                        match=MatchValue(value=filter_params["orientation"])
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)

        # Search in collection
        search_result = self._client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
        )
        
        # Format results
        results = []
        for scored_point in search_result:
            if scored_point.score >= SIMILARITY_THRESHOLD:
                result = scored_point.payload
                result["score"] = round(scored_point.score, 4)
                results.append(result)
        
        return results


# Singleton instance
rag_service = RAGService.get_instance()
