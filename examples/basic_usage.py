"""
Basic usage examples for StealthOCR
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from stealth_ocr import StealthOCR
import cv2
import numpy as np


def example_basic_ocr():
    """Basic OCR example"""
    print("=== Basic OCR Example ===")
    
    # Initialize OCR
    ocr = StealthOCR()
    
    # Create a simple test image with text
    # In a real scenario, you would load an actual image
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, "Hello StealthOCR!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Save test image
    cv2.imwrite('test_image.jpg', img)
    print("Created test image: test_image.jpg")
    
    # Extract text using Tesseract
    text_tesseract = ocr.extract_text('test_image.jpg', engine='tesseract')
    print(f"Tesseract result: '{text_tesseract}'")
    
    # Extract text using EasyOCR
    text_easyocr = ocr.extract_text('test_image.jpg', engine='easyocr')
    print(f"EasyOCR result: '{text_easyocr}'")
    
    # Get confidence scores
    confidence = ocr.get_text_confidence('test_image.jpg')
    print(f"Confidence scores: {confidence}")


def example_batch_processing():
    """Batch processing example"""
    print("\n=== Batch Processing Example ===")
    
    ocr = StealthOCR()
    
    # Create multiple test images
    test_files = []
    for i in range(3):
        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, f"Test Image {i+1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        filename = f'test_image_{i+1}.jpg'
        cv2.imwrite(filename, img)
        test_files.append(filename)
    
    print(f"Created {len(test_files)} test images")
    
    # Process all images
    results = ocr.batch_process(test_files, engine='tesseract')
    
    for file_path, text in results.items():
        print(f"{file_path}: '{text}'")


def example_image_preprocessing():
    """Image preprocessing example"""
    print("\n=== Image Preprocessing Example ===")
    
    ocr = StealthOCR()
    
    # Create a noisy test image
    img = np.ones((150, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, "Noisy Text Example", (50, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Add some noise
    noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
    noisy_img = cv2.add(img, noise)
    
    cv2.imwrite('noisy_image.jpg', noisy_img)
    print("Created noisy test image: noisy_image.jpg")
    
    # Show preprocessing effect
    processed = ocr.preprocess_image(noisy_img)
    cv2.imwrite('processed_image.jpg', processed)
    print("Created processed image: processed_image.jpg")
    
    # Extract text from both
    text_noisy = ocr.extract_text('noisy_image.jpg', engine='tesseract')
    text_processed = ocr.extract_text('processed_image.jpg', engine='tesseract')
    
    print(f"Noisy image text: '{text_noisy}'")
    print(f"Processed image text: '{text_processed}'")


if __name__ == "__main__":
    print("StealthOCR Examples")
    print("==================")
    
    try:
        example_basic_ocr()
        example_batch_processing()
        example_image_preprocessing()
        
        print("\n=== Cleanup ===")
        # Clean up test files
        test_files = ['test_image.jpg', 'test_image_1.jpg', 'test_image_2.jpg', 
                     'test_image_3.jpg', 'noisy_image.jpg', 'processed_image.jpg']
        
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed: {file}")
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have Tesseract installed and the virtual environment activated.")