"""Test script for S4 embedding functionality."""

import io
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from s4.embedding.openai_embeddings import OpenAIEmbeddings
    from s4.embedding.document_processor import DocumentProcessor
    from s4.embedding.search import SearchIndex
    from s4 import config
except ImportError as e:
    logger.error(f"Error importing S4 modules: {e}")
    sys.exit(1)

def test_embedding_generation():
    """Test OpenAI embedding generation."""
    try:
        embeddings = OpenAIEmbeddings()
        test_text = "This is a test document for embedding generation."
        embedding = embeddings.embed_text(test_text)
        
        logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
        return True
    except Exception as e:
        logger.error(f"Error testing embedding generation: {e}")
        return False

def test_document_processing():
    """Test document processing and text extraction."""
    try:
        processor = DocumentProcessor()
        
        text_content = "This is a test document for processing."
        result = processor.process_document(
            io.BytesIO(text_content.encode()), 
            "test.txt", 
            "text/plain"
        )
        
        logger.info(f"Extracted text: {result['text']}")
        logger.info(f"Embedding length: {len(result['embedding'])}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing document processing: {e}")
        return False

def test_search_index():
    """Test search index functionality."""
    try:
        search_index = SearchIndex()
        
        doc_id = "test-doc-1"
        text = "This is a test document for the search index."
        metadata = {"filename": "test.txt", "content_type": "text/plain"}
        
        success = search_index.add_document(doc_id, text, metadata)
        logger.info(f"Added document to search index: {success}")
        
        results = search_index.search("test document")
        logger.info(f"Search results: {len(results)} documents found")
        
        if len(results) > 0:
            logger.info(f"Top result score: {results[0]['score']}")
        
        success = search_index.remove_document(doc_id)
        logger.info(f"Removed document from search index: {success}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing search index: {e}")
        return False

if __name__ == "__main__":
    if os.path.exists(os.path.join(os.path.dirname(__file__), ".env")):
        logger.info("Loading environment variables from .env file")
        from dotenv import load_dotenv
        load_dotenv()
    
    logger.info("Starting embedding tests")
    
    embedding_test = test_embedding_generation()
    logger.info(f"Embedding generation test: {'PASSED' if embedding_test else 'FAILED'}")
    
    processing_test = test_document_processing()
    logger.info(f"Document processing test: {'PASSED' if processing_test else 'FAILED'}")
    
    search_test = test_search_index()
    logger.info(f"Search index test: {'PASSED' if search_test else 'FAILED'}")
    
    if embedding_test and processing_test and search_test:
        logger.info("All tests PASSED")
        sys.exit(0)
    else:
        logger.error("Some tests FAILED")
        sys.exit(1)
