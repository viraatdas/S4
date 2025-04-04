"""Search functionality for S4."""

import logging
import os
import json
from typing import Dict, List, Optional, Union, Any

import numpy as np

from s4.embedding.openai_embeddings import OpenAIEmbeddings
from s4 import config

logger = logging.getLogger(__name__)

class SearchIndex:
    """Search index for S4."""
    
    def __init__(
        self,
        embeddings_provider: Optional[OpenAIEmbeddings] = None,
        index_path: Optional[str] = None
    ):
        """Initialize search index.
        
        Args:
            embeddings_provider: Optional embeddings provider
            index_path: Optional path to store the index
        """
        self.embeddings_provider = embeddings_provider or OpenAIEmbeddings()
        self.index_path = index_path or os.path.join(config.DATA_DIR, "search_index.json")
        self.index = self._load_index()
        
    def _load_index(self) -> Dict:
        """Load the search index from disk.
        
        Returns:
            Dict: The search index
        """
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading search index: {e}")
                return {"documents": {}}
        else:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            return {"documents": {}}
            
    def _save_index(self):
        """Save the search index to disk."""
        try:
            with open(self.index_path, 'w') as f:
                json.dump(self.index, f)
        except Exception as e:
            logger.error(f"Error saving search index: {e}")
            
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the search index.
        
        Args:
            doc_id: Document ID
            text: Document text
            metadata: Document metadata
            
        Returns:
            bool: True if successful
        """
        try:
            embedding = self.embeddings_provider.embed_text(text)
            
            self.index["documents"][doc_id] = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata
            }
            
            self._save_index()
            
            logger.info(f"Added document {doc_id} to search index")
            return True
        except Exception as e:
            logger.error(f"Error adding document to search index: {e}")
            return False
            
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the search index.
        
        Args:
            doc_id: Document ID
            
        Returns:
            bool: True if successful
        """
        if doc_id in self.index["documents"]:
            try:
                del self.index["documents"][doc_id]
                self._save_index()
                logger.info(f"Removed document {doc_id} from search index")
                return True
            except Exception as e:
                logger.error(f"Error removing document from search index: {e}")
                return False
        else:
            logger.warning(f"Document {doc_id} not found in search index")
            return False
            
    def search(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7
    ) -> List[Dict]:
        """Search the index for documents matching the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List[Dict]: Search results
        """
        try:
            query_embedding = self.embeddings_provider.embed_text(query)
            
            results = []
            for doc_id, doc in self.index["documents"].items():
                similarity = self._calculate_similarity(query_embedding, doc["embedding"])
                if similarity >= threshold:
                    results.append({
                        "id": doc_id,
                        "text": doc["text"],
                        "metadata": doc["metadata"],
                        "score": similarity
                    })
                    
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
            
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            float: Similarity score
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)
