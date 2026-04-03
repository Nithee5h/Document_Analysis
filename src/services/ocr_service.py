from pathlib import Path
import pytesseract
from PIL import Image
import logging
from src.core.config import settings
from src.services.preprocess import ImagePreprocessor
from src.services.google_vision_ocr import GoogleVisionOCRService

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self) -> None:
        try:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        except Exception as e:
            logger.warning(f"Could not set Tesseract path: {e}")
        self.preprocessor = ImagePreprocessor()
        self.google_vision = GoogleVisionOCRService()

    def extract_text(self, image_path: Path) -> tuple[str, bool, str]:
        """
        Extract text using best available OCR service.
        Try Google Cloud Vision first, then Tesseract.
        Returns: (text, ocr_used, ocr_method)
        """
        # Try Google Cloud Vision first (if available)
        if self.google_vision.is_available() and settings.use_google_vision:
            logger.info("Attempting Google Cloud Vision OCR...")
            text, success = self.google_vision.extract_text(image_path)
            if success and text and len(text.strip()) > 0:
                return text, True, "vision_api"
        
        # Fall back to Tesseract-based OCR
        logger.info("Using Tesseract OCR...")
        text, used = self._tesseract_extract(image_path)
        return text, used, "tesseract"
    
    def _tesseract_extract(self, image_path: Path) -> tuple[str, bool]:
        """Extract text using Tesseract OCR with multiple strategies."""
        try:
            # First, validate that we can load the image at all
            try:
                test_img = Image.open(image_path)
                test_img.verify()
            except Exception as e:
                logger.error(f"Image file cannot be loaded or is corrupted: {image_path} - {str(e)}")
                raise ValueError(f"Image file cannot be loaded or is corrupted: {str(e)}")
            
            # Strategy 1: Try with preprocessed image first
            try:
                processed = self.preprocessor.preprocess(image_path)
                temp_path = image_path.with_suffix(".ocr.png")
                Image.fromarray(processed).save(temp_path)
                
                # Try multiple configurations on preprocessed image
                text = self._try_tesseract_configs(temp_path)
                
                # Clean up temp file
                try:
                    temp_path.unlink()
                except:
                    pass
                    
                if text and len(text.strip()) > 5:
                    logger.info(f"OCR successful with preprocessing: {len(text)} chars")
                    text = self._clean_ocr_text(text)
                    return text, True
            except Exception as e:
                logger.warning(f"Preprocessing strategy failed: {e}")
            
            # Strategy 2: Try directly on original image with optimized configs
            logger.info("Trying direct OCR on original image...")
            text = self._try_tesseract_configs_optimized(image_path)
            
            if text and len(text.strip()) > 5:
                logger.info(f"OCR successful without preprocessing: {len(text)} chars")
                text = self._clean_ocr_text(text)
                return text, True
            
            # Fallback: basic OCR
            logger.warning("All strategies failed, using basic OCR")
            text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
            text = self._clean_ocr_text(text)
            return text, True
            
        except Exception as e:
            logger.error(f"Tesseract OCR extraction failed: {e}")
            raise ValueError(f"OCR processing failed: {str(e)}")
    
    def _try_tesseract_configs(self, image_path: Path) -> str:
        """Try multiple Tesseract configurations on preprocessed image."""
        configs = [
            "--oem 1 --psm 3",      # Legacy engine, auto page segmentation
            "--oem 3 --psm 6",      # LSTM engine, single uniform block
            "--oem 2 --psm 4",      # Combined engines, single column
        ]
        
        for config in configs:
            try:
                result = pytesseract.image_to_string(
                    Image.open(image_path),
                    config=config,
                    lang='eng'
                )
                if result and len(result.strip()) > 10:
                    logger.info(f"Success with config: {config}")
                    return result
            except Exception as e:
                logger.debug(f"Config {config} failed: {e}")
                continue
        
        return ""
    
    def _try_tesseract_configs_optimized(self, image_path: Path) -> str:
        """Try optimized Tesseract configurations for original images (JPG)."""
        # These configs work better for photos and natural images
        configs = [
            "--oem 3 --psm 6",      # LSTM, single block (good for photos)
            "--oem 3 --psm 3",      # LSTM, auto segmentation  
            "--oem 1 --psm 3",      # Legacy, auto segmentation
            "",                     # Default configuration
        ]
        
        for config in configs:
            try:
                result = pytesseract.image_to_string(
                    Image.open(image_path),
                    config=config,
                    lang='eng'
                )
                if result and len(result.strip()) > 10:
                    logger.info(f"Success with direct config: {config}")
                    return result
            except Exception as e:
                logger.debug(f"Direct config {config} failed: {e}")
                continue
        
        return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean up OCR errors and filter corrupted text."""
        import re
        
        if not text or len(text.strip()) < 5:
            return ""
        
        # Step 1: Simple character fixes
        replacements = {
            r'[`ˋ]': "'",
            r'rn': 'm',  # Common: 'rn' read as 'm'
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        # Step 2: Filter out completely corrupted lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 2:
                continue
            
            # Skip lines that are clearly corrupted
            # Count alphanumeric vs special characters
            alpha_count = sum(1 for c in line if c.isalnum() or c.isspace())
            special_count = sum(1 for c in line if c in '!@#$%^&*()[]{}|\\<>~`')
            
            # If more than 30% special chars, it's likely garbage
            total = len(line)
            if total > 0 and special_count / total > 0.3:
                logger.debug(f"Skipping corrupted line: {line}")
                continue
            
            # Skip lines with too many repeated characters
            if re.search(r'(.)\\1{5,}', line):  # 6+ repeated same char
                logger.debug(f"Skipping line with repetition: {line}")
                continue
            
            # Strip excessive special characters from edges
            line = re.sub(r'^[_\-=\[\]{}|\\]+', '', line)
            line = re.sub(r'[_\-=\[\]{}|\\]+$', '', line)
            
            if line:  # Only add if still has content
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # Step 3: Validate result quality
        if result and len(result.strip()) > 5:
            return result
        else:
            logger.warning("Text after cleaning is too short/empty")
            return ""