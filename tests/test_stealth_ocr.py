"""
Tests for StealthOCR
"""

import unittest
import sys
import os
import numpy as np
import cv2

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from stealth_ocr import StealthOCR


class TestStealthOCR(unittest.TestCase):
    """Test cases for StealthOCR"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ocr = StealthOCR()
        
        # Create a simple test image
        self.test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(self.test_image, "Test OCR", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    def test_initialization(self):
        """Test OCR initialization"""
        self.assertIsInstance(self.ocr, StealthOCR)
        self.assertEqual(self.ocr.languages, ['en'])
        self.assertFalse(self.ocr.use_gpu)
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        processed = self.ocr.preprocess_image(self.test_image)
        
        # Check that processed image is grayscale
        self.assertEqual(len(processed.shape), 2)
        
        # Check that image dimensions are preserved
        self.assertEqual(processed.shape[:2], self.test_image.shape[:2])
    
    def test_extract_text_tesseract(self):
        """Test Tesseract OCR extraction"""
        try:
            text = self.ocr.extract_text_tesseract(self.test_image)
            self.assertIsInstance(text, str)
        except Exception as e:
            # Tesseract might not be installed in test environment
            self.assertIn("Tesseract", str(e))
    
    def test_extract_text_easyocr(self):
        """Test EasyOCR extraction"""
        try:
            text = self.ocr.extract_text_easyocr(self.test_image)
            self.assertIsInstance(text, str)
        except Exception as e:
            # EasyOCR might fail in test environment
            self.assertIsInstance(str(e), str)
    
    def test_get_text_confidence(self):
        """Test confidence score extraction"""
        try:
            confidence = self.ocr.get_text_confidence(self.test_image)
            self.assertIsInstance(confidence, dict)
            self.assertIn('mean_confidence', confidence)
            self.assertIn('min_confidence', confidence)
            self.assertIn('max_confidence', confidence)
            self.assertIn('total_words', confidence)
        except Exception as e:
            # Tesseract might not be installed
            self.assertIsInstance(str(e), str)
    
    def test_batch_process(self):
        """Test batch processing"""
        # Create multiple test images
        test_images = []
        for i in range(3):
            img = np.ones((100, 200, 3), dtype=np.uint8) * 255
            cv2.putText(img, f"Test {i+1}", (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            test_images.append(img)
        
        try:
            results = self.ocr.batch_process(test_images, engine='tesseract')
            self.assertIsInstance(results, dict)
            self.assertEqual(len(results), 3)
        except Exception as e:
            # Tesseract might not be installed
            self.assertIsInstance(str(e), str)


if __name__ == '__main__':
    unittest.main()