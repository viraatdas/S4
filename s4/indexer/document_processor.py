"""Document processor for extracting text from different file types."""

import io
import logging
import mimetypes
import os
from typing import Dict, List, Optional, BinaryIO, Tuple, Union

from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Extract and process text from various document types."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the document processor.
        
        Args:
            chunk_size: Size of text chunks for indexing
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
    def process_document(
        self, 
        file_obj: Union[BinaryIO, bytes, io.BytesIO],
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> List[str]:
        """Process a document and extract text chunks.
        
        Args:
            file_obj: File object or bytes
            file_name: Optional file name to help determine type
            mime_type: Optional MIME type to specify file type
            
        Returns:
            List[str]: List of text chunks
        """
        # Determine MIME type
        if not mime_type and file_name:
            mime_type, _ = mimetypes.guess_type(file_name)
            
        if not mime_type:
            # Default to plain text if we can't determine
            mime_type = 'text/plain'
            
        # Extract text based on MIME type
        text = self._extract_text(file_obj, mime_type)
        
        if not text:
            logger.warning(f"No text extracted from document: {file_name or 'unnamed'}")
            return []
            
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        logger.info(f"Processed document into {len(chunks)} chunks")
        return chunks
    
    def _extract_text(self, file_obj: Union[BinaryIO, bytes, io.BytesIO], mime_type: str) -> str:
        """Extract text from a file based on its MIME type.
        
        Args:
            file_obj: File object or bytes
            mime_type: MIME type of the file
            
        Returns:
            str: Extracted text
        """
        # Ensure we have bytes to work with
        if isinstance(file_obj, io.BytesIO):
            file_bytes = file_obj.getvalue()
        elif isinstance(file_obj, bytes):
            file_bytes = file_obj
        else:
            # Read from file-like object
            file_bytes = file_obj.read()
            
        # Handle different file types
        if mime_type.startswith('text/'):
            # Plain text files
            try:
                return file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return file_bytes.decode('latin-1')
                except Exception as e:
                    logger.error(f"Error decoding text file: {e}")
                    return ""
                    
        elif mime_type == 'application/pdf':
            # PDF files
            try:
                # Only import if needed
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                logger.error("PyPDF2 package not installed. Cannot process PDF files.")
                return ""
            except Exception as e:
                logger.error(f"Error processing PDF file: {e}")
                return ""
                
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            # Word documents
            try:
                # Only import if needed
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
                return text
            except ImportError:
                logger.error("python-docx package not installed. Cannot process Word files.")
                return ""
            except Exception as e:
                logger.error(f"Error processing Word file: {e}")
                return ""
                
        elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            # Excel files
            try:
                # Only import if needed
                import pandas as pd
                df = pd.read_excel(io.BytesIO(file_bytes))
                return df.to_string()
            except ImportError:
                logger.error("pandas package not installed. Cannot process Excel files.")
                return ""
            except Exception as e:
                logger.error(f"Error processing Excel file: {e}")
                return ""
                
        elif mime_type == 'application/json':
            # JSON files
            try:
                import json
                data = json.loads(file_bytes)
                # Pretty print to make it more readable
                return json.dumps(data, indent=2)
            except Exception as e:
                logger.error(f"Error processing JSON file: {e}")
                return ""
                
        elif mime_type in ['application/x-yaml', 'text/yaml']:
            # YAML files
            try:
                # Only import if needed
                import yaml
                data = yaml.safe_load(file_bytes)
                # Convert to string representation
                return yaml.dump(data)
            except ImportError:
                logger.error("PyYAML package not installed. Cannot process YAML files.")
                return ""
            except Exception as e:
                logger.error(f"Error processing YAML file: {e}")
                return ""
                
        else:
            # Unsupported file type
            logger.warning(f"Unsupported MIME type: {mime_type}")
            
            # Try to decode as text as fallback
            try:
                return file_bytes.decode('utf-8')
            except:
                try:
                    return file_bytes.decode('latin-1')
                except:
                    return "" 