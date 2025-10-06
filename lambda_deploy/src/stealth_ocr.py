"""
StealthOCR - A powerful and stealthy OCR toolkit
"""

import cv2
import pytesseract
import easyocr
import numpy as np
from PIL import Image
import os
from typing import List, Dict, Union, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthOCR:
    """
    Main OCR class that provides multiple OCR engines and preprocessing capabilities
    """
    
    def __init__(self, 
                 tesseract_path: Optional[str] = None,
                 languages: List[str] = ['eng'],
                 use_gpu: bool = False):
        """
        Initialize StealthOCR
        
        Args:
            tesseract_path: Path to tesseract executable
            languages: List of languages for OCR
            use_gpu: Whether to use GPU acceleration for EasyOCR
        """
        self.languages = languages
        self.use_gpu = use_gpu
        
        # Set tesseract path if provided, otherwise try to find it
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Try common Tesseract paths
            import shutil
            tesseract_cmd = shutil.which('tesseract')
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            else:
                # Try macOS Homebrew path
                if os.path.exists('/opt/homebrew/bin/tesseract'):
                    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
                elif os.path.exists('/usr/local/bin/tesseract'):
                    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        
        # Set TESSDATA_PREFIX environment variable
        import os
        if not os.environ.get('TESSDATA_PREFIX'):
            # Try common tessdata paths
            tessdata_paths = [
                '/opt/homebrew/share/tessdata',
                '/usr/local/share/tessdata',
                '/usr/share/tessdata'
            ]
            for path in tessdata_paths:
                if os.path.exists(path):
                    os.environ['TESSDATA_PREFIX'] = path
                    break
        
        # Initialize EasyOCR reader
        self.easyocr_reader = None
        # Convert Tesseract language codes to EasyOCR codes
        easyocr_langs = []
        for lang in languages:
            if lang == 'eng':
                easyocr_langs.append('en')
            elif lang == 'spa':
                easyocr_langs.append('es')
            elif lang == 'fra':
                easyocr_langs.append('fr')
            elif lang == 'deu':
                easyocr_langs.append('de')
            else:
                easyocr_langs.append(lang)
        
        if easyocr_langs:
            self.easyocr_reader = easyocr.Reader(easyocr_langs, gpu=use_gpu)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_tesseract(self, image: Union[str, np.ndarray]) -> str:
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Image path or numpy array
            
        Returns:
            Extracted text
        """
        try:
            if isinstance(image, str):
                image = cv2.imread(image)
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed, lang='+'.join(self.languages))
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Union[str, np.ndarray]) -> str:
        """
        Extract text using EasyOCR
        
        Args:
            image: Image path or numpy array
            
        Returns:
            Extracted text
        """
        try:
            if self.easyocr_reader is None:
                logger.warning("EasyOCR reader not initialized")
                return ""
            
            if isinstance(image, str):
                image = cv2.imread(image)
            
            # Extract text
            results = self.easyocr_reader.readtext(image)
            
            # Combine all detected text
            text = ' '.join([result[1] for result in results])
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return ""
    
    def extract_text(self, 
                    image: Union[str, np.ndarray], 
                    engine: str = 'tesseract') -> str:
        """
        Extract text from image using specified engine
        
        Args:
            image: Image path or numpy array
            engine: OCR engine to use ('tesseract' or 'easyocr')
            
        Returns:
            Extracted text
        """
        if engine.lower() == 'tesseract':
            return self.extract_text_tesseract(image)
        elif engine.lower() == 'easyocr':
            return self.extract_text_easyocr(image)
        else:
            raise ValueError(f"Unsupported OCR engine: {engine}")
    
    def batch_process(self, 
                     file_paths: List[str], 
                     engine: str = 'tesseract') -> Dict[str, str]:
        """
        Process multiple files in batch
        
        Args:
            file_paths: List of file paths to process
            engine: OCR engine to use
            
        Returns:
            Dictionary mapping file paths to extracted text
        """
        results = {}
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing: {file_path}")
                text = self.extract_text(file_path, engine)
                results[file_path] = text
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results[file_path] = ""
        
        return results
    
    def get_text_confidence(self, image: Union[str, np.ndarray]) -> Dict[str, float]:
        """
        Get confidence scores for extracted text
        
        Args:
            image: Image path or numpy array
            
        Returns:
            Dictionary with confidence scores
        """
        try:
            if isinstance(image, str):
                image = cv2.imread(image)
            
            processed = self.preprocess_image(image)
            
            # Get detailed data including confidence
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return {
                    'mean_confidence': np.mean(confidences),
                    'min_confidence': np.min(confidences),
                    'max_confidence': np.max(confidences),
                    'total_words': len(confidences)
                }
            else:
                return {'mean_confidence': 0, 'min_confidence': 0, 'max_confidence': 0, 'total_words': 0}
        
        except Exception as e:
            logger.error(f"Failed to get confidence scores: {e}")
            return {'mean_confidence': 0, 'min_confidence': 0, 'max_confidence': 0, 'total_words': 0}


def main():
    """
    Example usage of StealthOCR
    """
    # Initialize OCR
    ocr = StealthOCR()
    
    # Example with a test image (you'll need to provide an actual image)
    print("StealthOCR initialized successfully!")
    print("Available OCR engines: tesseract, easyocr")
    print("Use ocr.extract_text('path/to/image.jpg', engine='tesseract') to extract text")


if __name__ == "__main__":
    main()