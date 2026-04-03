"""
Google Cloud Vision OCR Service
Provides high-accuracy OCR using Google Cloud Vision API
"""
from pathlib import Path
import logging
import os
from typing import Optional
from google.cloud import vision
from src.core.config import settings

logger = logging.getLogger(__name__)


class GoogleVisionOCRService:
    """
    High-accuracy OCR using Google Cloud Vision API.
    
    Setup required:
    1. Create Google Cloud Project
    2. Enable Vision API
    3. Create Service Account with Vision permissions
    4. Download JSON credentials
    5. Set GOOGLE_APPLICATION_CREDENTIALS env var or use config
    """
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Cloud Vision client."""
        try:
            # Try to use credentials from environment or config
            if settings.google_credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_credentials_path
            
            # Check if credentials are available
            if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or settings.google_credentials_path:
                self.client = vision.ImageAnnotatorClient()
                self.enabled = True
                logger.info("✅ Google Cloud Vision API initialized successfully")
            else:
                logger.warning("⚠️ Google Cloud Vision not configured - using Tesseract fallback")
                self.enabled = False
        except Exception as e:
            logger.warning(f"⚠️ Google Cloud Vision initialization failed: {e}")
            logger.info("   Falling back to Tesseract OCR")
            self.enabled = False
    
    def extract_text(self, image_path: Path) -> tuple[str, bool]:
        """
        Extract text from image using Google Cloud Vision API.
        
        Args:
            image_path: Path to image file
            
        Returns:
            tuple: (extracted_text, ocr_used)
        """
        if not self.enabled or not self.client:
            return "", False
        
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = vision.Image(content=content)
            
            # Perform OCR
            response = self.client.document_text_detection(image=image)
            
            # Extract text
            text = ""
            if response.full_text_annotation:
                text = response.full_text_annotation.text
            
            if response.error.message:
                logger.error(f"Google Vision API error: {response.error.message}")
                return "", False
            
            logger.info(f"✅ Google Cloud Vision extracted {len(text)} characters")
            return text, True
            
        except Exception as e:
            logger.error(f"Google Cloud Vision OCR failed: {e}")
            return "", False
    
    def is_available(self) -> bool:
        """Check if Google Cloud Vision is available."""
        return self.enabled and self.client is not None
