"""Document index for S4 with vector database functionality."""

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

from s4 import config
from s4.exceptions import IndexError

logger = logging.getLogger(__name__)

class DocumentIndex:
    """Document index using vector embeddings for semantic search."""
    
    def __init__(
        self, 
        index_id: str = "default",
        tenant_id: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """Initialize the document index.
        
        Args:
            index_id: Unique identifier for this index
            tenant_id: Optional tenant ID for multi-tenant mode
            openai_api_key: Optional OpenAI API key
        """
        self.index_id = index_id
        self.tenant_id = tenant_id
        
        # Adjust index ID based on tenant (if in multi-tenant mode)
        self.full_index_id = index_id
        if tenant_id:
            self.full_index_id = f"{tenant_id}_{index_id}"
            
        # Initialize embeddings with provided API key or default
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=openai_api_key or config.OPENAI_API_KEY
        )
        
        # Set up paths for index storage
        self.index_path = config.INDEX_STORAGE_PATH / f"{self.full_index_id}.faiss"
        self.metadata_path = config.INDEX_STORAGE_PATH / f"{self.full_index_id}.json"
        
        # Create or load the index
        self.index = self._load_or_create_index()
        self.metadata = self._load_or_create_metadata()
    
    def _load_or_create_index(self) -> FAISS:
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path):
            logger.info(f"Loading existing index from {self.index_path}")
            try:
                index = FAISS.load_local(
                    folder_path=str(self.index_path.parent),
                    index_name=self.index_path.stem,
                    embeddings=self.embeddings
                )
                return index
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                logger.info("Creating new index")
        
        # Create new index with empty document list
        return FAISS.from_texts([""], self.embeddings)
    
    def _load_or_create_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load existing metadata or create a new metadata store."""
        if os.path.exists(self.metadata_path):
            logger.info(f"Loading existing metadata from {self.metadata_path}")
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                logger.info("Creating new metadata store")
        
        # Create new empty metadata store
        return {}
    
    def _save_metadata(self):
        """Save metadata to disk."""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    
    def add_document(
        self, 
        file_id: str, 
        chunks: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a document to the index.
        
        Args:
            file_id: Unique identifier for the file
            chunks: List of text chunks to index
            metadata: Optional metadata about the file
        """
        if not chunks:
            logger.warning(f"No chunks to index for file {file_id}")
            return
            
        # Add metadata
        if not metadata:
            metadata = {}
            
        # Add tenant info to metadata if in multi-tenant mode
        if self.tenant_id and 'tenant_id' not in metadata:
            metadata['tenant_id'] = self.tenant_id
            
        self.metadata[file_id] = {
            'chunk_count': len(chunks),
            'metadata': metadata
        }
        
        # Create document-specific metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'file_id': file_id,
                'chunk_index': i,
                'chunk_count': len(chunks),
                **metadata
            }
            chunk_metadatas.append(chunk_metadata)
            
        # Add chunks to index
        try:
            self.index.add_texts(chunks, metadatas=chunk_metadatas)
            logger.info(f"Added {len(chunks)} chunks for file {file_id} to the index")
            
            # Save metadata
            self._save_metadata()
            
            # Save index
            self.index.save_local(
                folder_path=str(self.index_path.parent),
                index_name=self.index_path.stem
            )
        except Exception as e:
            logger.error(f"Error adding document to index: {e}")
            raise IndexError(f"Error adding document to index: {str(e)}")
    
    def remove_document(self, file_id: str):
        """Remove a document from the index.
        
        Args:
            file_id: Unique identifier for the file to remove
        """
        if file_id not in self.metadata:
            logger.warning(f"File {file_id} not found in index")
            return
            
        # Since FAISS doesn't support removal, we need to rebuild the index
        # Get all documents except the one to remove
        all_docs = []
        all_metadatas = []
        
        # Find documents that are not the one to remove
        for i, metadata in enumerate(self.index.docstore._dict.values()):
            if metadata.metadata.get('file_id') != file_id:
                all_docs.append(metadata.page_content)
                all_metadatas.append(metadata.metadata)
        
        # Create new index with remaining documents
        if all_docs:
            new_index = FAISS.from_texts(all_docs, self.embeddings, metadatas=all_metadatas)
            self.index = new_index
        else:
            # If no documents left, create an empty index
            self.index = FAISS.from_texts([""], self.embeddings)
            
        # Remove from metadata
        del self.metadata[file_id]
        self._save_metadata()
        
        # Save index
        self.index.save_local(
            folder_path=str(self.index_path.parent),
            index_name=self.index_path.stem
        )
        
        logger.info(f"Removed file {file_id} from index")
    
    def search(
        self, 
        query: str, 
        limit: int = 5,
        filter_by_file_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search the index for documents matching the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            filter_by_file_id: Optional file ID to restrict search to
            
        Returns:
            List of dictionaries with document chunks and metadata
        """
        # Define filter function based on criteria
        filter_conditions = []
        
        # Add tenant filter if in multi-tenant mode
        if self.tenant_id:
            filter_conditions.append(lambda metadata: metadata.get('tenant_id') == self.tenant_id)
            
        # Add file ID filter if specified
        if filter_by_file_id:
            filter_conditions.append(lambda metadata: metadata.get('file_id') == filter_by_file_id)
           
        # Combine filters if needed
        filter_fn = None
        if filter_conditions:
            if len(filter_conditions) == 1:
                filter_fn = filter_conditions[0]
            else:
                # Apply all filters (logical AND)
                filter_fn = lambda metadata: all(
                    condition(metadata) for condition in filter_conditions
                )
            
        # Perform the search
        try:
            results = self.index.similarity_search_with_score(
                query, 
                k=limit,
                filter=filter_fn
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'score': float(score),  # Convert numpy float to Python float
                    'metadata': doc.metadata
                })
                
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise IndexError(f"Error searching index: {str(e)}")
    
    def get_document_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a document.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self.metadata.get(file_id)
        
    def get_document_count(self) -> int:
        """Get the number of documents in the index.
        
        Returns:
            int: Number of documents
        """
        return len(self.metadata)
        
    def get_index_size(self) -> int:
        """Get the size of the index in bytes.
        
        Returns:
            int: Size in bytes
        """
        if self.index_path.exists():
            return os.path.getsize(self.index_path)
        return 0 