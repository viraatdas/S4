"""OpenAI embeddings implementation for S4."""

import logging
import os
from typing import List, Dict, Any, Optional, Union

import openai
from openai import OpenAI

from s4 import config

logger = logging.getLogger(__name__)

class OpenAIEmbeddings:
    """OpenAI embeddings implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize OpenAI embeddings.
        
        Args:
            api_key: Optional OpenAI API key
            model: Optional embedding model name
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.EMBEDDING_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI embeddings with model: {self.model}")
        
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
            
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
            
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)
