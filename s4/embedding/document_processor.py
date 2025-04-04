"""Document processor for extracting text and generating embeddings."""

import io
import logging
import os
from typing import Dict, List, Optional, Union, BinaryIO, Tuple

import docx
import PyPDF2
from PIL import Image
import pytesseract

from s4.embedding.openai_embeddings import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processor for extracting text and generating embeddings."""
    
    def __init__(self, embeddings_provider: Optional[OpenAIEmbeddings] = None):
        """Initialize document processor.
        
        Args:
            embeddings_provider: Optional embeddings provider
        """
        self.embeddings_provider = embeddings_provider or OpenAIEmbeddings()
        
    def process_document(
        self, 
        file_content: Union[BinaryIO, bytes], 
        file_name: str,
        content_type: Optional[str] = None
    ) -> Dict:
        """Process a document to extract text and generate embeddings.
        
        Args:
            file_content: File content as bytes or file-like object
            file_name: Name of the file
            content_type: Optional MIME type
            
        Returns:
            Dict: Document processing results with text and embeddings
        """
        if not content_type:
            ext = os.path.splitext(file_name)[1].lower()
            if ext == '.pdf':
                content_type = 'application/pdf'
            elif ext == '.docx':
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif ext == '.txt':
                content_type = 'text/plain'
            elif ext in ['.jpg', '.jpeg', '.png']:
                content_type = f'image/{ext[1:]}'
                
        text = self._extract_text(file_content, content_type)
        
        if not text:
            logger.warning(f"No text extracted from {file_name}")
            return {
                "text": "",
                "embedding": [],
                "tokens": 0
            }
            
        embedding = self.embeddings_provider.embed_text(text)
        
        tokens = len(text.split()) * 1.3  # Rough estimate
        
        return {
            "text": text,
            "embedding": embedding,
            "tokens": int(tokens)
        }
        
    def _extract_text(self, file_content: Union[BinaryIO, bytes], content_type: str) -> str:
        """Extract text from a file based on its content type.
        
        Args:
            file_content: File content as bytes or file-like object
            content_type: MIME type of the file
            
        Returns:
            str: Extracted text
        """
        if not isinstance(file_content, io.BytesIO):
            if isinstance(file_content, bytes):
                file_content = io.BytesIO(file_content)
            else:
                file_content = io.BytesIO(file_content.read())
                file_content.seek(0)
                
        if content_type == 'application/pdf':
            return self._extract_text_from_pdf(file_content)
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self._extract_text_from_docx(file_content)
        elif content_type.startswith('text/'):
            return file_content.read().decode('utf-8', errors='ignore')
        elif content_type.startswith('image/'):
            return self._extract_text_from_image(file_content)
        else:
            logger.warning(f"Unsupported content type: {content_type}")
            return ""
            
    def _extract_text_from_pdf(self, file_content: io.BytesIO) -> str:
        """Extract text from a PDF file.
        
        Args:
            file_content: PDF file content
            
        Returns:
            str: Extracted text
        """
        try:
            reader = PyPDF2.PdfReader(file_content)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
            
    def _extract_text_from_docx(self, file_content: io.BytesIO) -> str:
        """Extract text from a DOCX file.
        
        Args:
            file_content: DOCX file content
            
        Returns:
            str: Extracted text
        """
        try:
            doc = docx.Document(file_content)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""
            
    def _extract_text_from_image(self, file_content: io.BytesIO) -> str:
        """Extract text from an image using OCR.
        
        Args:
            file_content: Image file content
            
        Returns:
            str: Extracted text
        """
        try:
            image = Image.open(file_content)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
