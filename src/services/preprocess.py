from pathlib import Path
import cv2
import numpy as np


class ImagePreprocessor:
    def preprocess(self, image_path: Path) -> np.ndarray:
        """
        Smart image preprocessing for better OCR quality.
        Uses conservative approach for JPG photos, more aggressive for scanned documents.
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Unable to read image file: {image_path} (file may be corrupted or in an unsupported format)")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Step 1: Upscale small images for better OCR (but not too much)
        height, width = gray.shape
        if width < 800 or height < 600:
            scale = max(1.5, 1200 / max(width, height))  # Conservative upscaling
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Step 2: Light denoising - use bilateral filter instead of aggressive NLM
        # This preserves text edges better
        denoised = cv2.bilateralFilter(gray, 5, 50, 50)
        
        # Step 3: Gentle contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Step 4: Return enhanced grayscale - DO NOT threshold!
        # Tesseract works better with grayscale than binary images
        return enhanced