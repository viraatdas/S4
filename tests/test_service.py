"""Tests for the S4 service."""

import io
import os
import unittest
from unittest.mock import patch, MagicMock

from s4.service import S4Service
from s4.storage import S3Storage
from s4.indexer import DocumentProcessor, DocumentIndex

class TestS4Service(unittest.TestCase):
    """Test cases for S4Service."""
    
    @patch('s4.storage.s3.S3Storage')
    @patch('s4.indexer.document_processor.DocumentProcessor')
    @patch('s4.indexer.index.DocumentIndex')
    def setUp(self, mock_index, mock_processor, mock_storage):
        """Set up test fixtures."""
        self.mock_storage = mock_storage.return_value
        self.mock_processor = mock_processor.return_value
        self.mock_index = mock_index.return_value
        self.service = S4Service()
        self.service.storage = self.mock_storage
        self.service.processor = self.mock_processor
        self.service.index = self.mock_index
        
    def test_upload_file_with_indexing(self):
        """Test uploading a file with indexing."""
        # Setup mocks
        test_file_content = b"test file content"
        test_file_obj = io.BytesIO(test_file_content)
        test_file_name = "test.txt"
        test_file_id = "test-uuid/test.txt"
        test_chunks = ["test file content"]
        
        self.mock_storage.upload_file.return_value = test_file_id
        self.mock_processor.process_document.return_value = test_chunks
        
        # Call the method
        result = self.service.upload_file(
            file_obj=test_file_obj,
            file_name=test_file_name,
            content_type="text/plain",
            index=True
        )
        
        # Assert results
        self.assertEqual(result["file_id"], test_file_id)
        self.assertEqual(result["file_name"], test_file_name)
        self.assertTrue(result["indexed"])
        
        # Assert method calls
        self.mock_storage.upload_file.assert_called_once()
        self.mock_processor.process_document.assert_called_once()
        self.mock_index.add_document.assert_called_once()
        
    def test_upload_file_without_indexing(self):
        """Test uploading a file without indexing."""
        # Setup mocks
        test_file_content = b"test file content"
        test_file_obj = io.BytesIO(test_file_content)
        test_file_name = "test.txt"
        test_file_id = "test-uuid/test.txt"
        
        self.mock_storage.upload_file.return_value = test_file_id
        
        # Call the method
        result = self.service.upload_file(
            file_obj=test_file_obj,
            file_name=test_file_name,
            content_type="text/plain",
            index=False
        )
        
        # Assert results
        self.assertEqual(result["file_id"], test_file_id)
        self.assertEqual(result["file_name"], test_file_name)
        self.assertFalse(result["indexed"])
        
        # Assert method calls
        self.mock_storage.upload_file.assert_called_once()
        self.mock_processor.process_document.assert_not_called()
        self.mock_index.add_document.assert_not_called()
        
    def test_search(self):
        """Test searching for documents."""
        # Setup mocks
        test_query = "test query"
        test_limit = 5
        test_results = [
            {
                "content": "test content",
                "score": 0.9,
                "metadata": {"file_id": "test-uuid/test.txt"}
            }
        ]
        
        self.mock_index.search.return_value = test_results
        
        # Call the method
        results = self.service.search(test_query, test_limit)
        
        # Assert results
        self.assertEqual(results, test_results)
        
        # Assert method calls
        self.mock_index.search.assert_called_once_with(
            test_query, test_limit, filter_by_file_id=None
        )
        
    def test_download_file(self):
        """Test downloading a file."""
        # Setup mocks
        test_file_id = "test-uuid/test.txt"
        test_file_content = io.BytesIO(b"test file content")
        test_metadata = {"content-type": "text/plain"}
        
        self.mock_storage.download_file.return_value = (test_file_content, test_metadata)
        
        # Call the method
        file_content, metadata = self.service.download_file(test_file_id)
        
        # Assert results
        self.assertEqual(file_content, test_file_content)
        self.assertEqual(metadata, test_metadata)
        
        # Assert method calls
        self.mock_storage.download_file.assert_called_once_with(test_file_id)
        
    def test_delete_file(self):
        """Test deleting a file."""
        # Setup mocks
        test_file_id = "test-uuid/test.txt"
        self.mock_storage.delete_file.return_value = True
        
        # Call the method
        result = self.service.delete_file(test_file_id)
        
        # Assert results
        self.assertTrue(result)
        
        # Assert method calls
        self.mock_storage.delete_file.assert_called_once_with(test_file_id)
        self.mock_index.remove_document.assert_called_once_with(test_file_id)

if __name__ == "__main__":
    unittest.main() 