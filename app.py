"""
Streamlit web application for StealthOCR
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
import cv2
import numpy as np
from PIL import Image
import io


def main():
    st.set_page_config(
        page_title="StealthOCR",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 StealthOCR")
    st.markdown("A powerful and stealthy OCR toolkit")
    
    # Initialize OCR
    if 'ocr' not in st.session_state:
        st.session_state.ocr = StealthOCR()
    
    # Sidebar for settings
    st.sidebar.header("Settings")
    engine = st.sidebar.selectbox("OCR Engine", ["tesseract", "easyocr"])
    languages = st.sidebar.multiselect("Languages", ["en", "es", "fr", "de"], default=["en"])
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Single Image", "Batch Processing", "About"])
    
    with tab1:
        st.header("Single Image OCR")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'tiff', 'bmp']
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Extract Text", type="primary"):
                    with st.spinner("Processing..."):
                        text = st.session_state.ocr.extract_text(img_array, engine=engine)
                        st.text_area("Extracted Text", text, height=200)
            
            with col2:
                if st.button("Get Confidence"):
                    with st.spinner("Analyzing..."):
                        confidence = st.session_state.ocr.get_text_confidence(img_array)
                        st.json(confidence)
    
    with tab2:
        st.header("Batch Processing")
        
        uploaded_files = st.file_uploader(
            "Choose multiple image files",
            type=['png', 'jpg', 'jpeg', 'tiff', 'bmp'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"Uploaded {len(uploaded_files)} files")
            
            if st.button("Process All Images", type="primary"):
                results = {}
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    image = Image.open(uploaded_file)
                    img_array = np.array(image)
                    if len(img_array.shape) == 3:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                    text = st.session_state.ocr.extract_text(img_array, engine=engine)
                    results[uploaded_file.name] = text
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Display results
                for filename, text in results.items():
                    with st.expander(f"📄 {filename}"):
                        st.text(text)
    
    with tab3:
        st.header("About StealthOCR")
        st.markdown("""
        **StealthOCR** is a powerful and stealthy Optical Character Recognition toolkit built with Python.
        
        ### Features:
        - Multiple OCR engines (Tesseract, EasyOCR)
        - Image preprocessing and enhancement
        - Batch processing capabilities
        - Web interface for easy interaction
        - High accuracy text extraction
        
        ### Supported Formats:
        - Images: PNG, JPG, JPEG, TIFF, BMP
        - Documents: PDF (coming soon)
        
        ### OCR Engines:
        - **Tesseract**: High accuracy for printed text
        - **EasyOCR**: Multi-language support with deep learning
        """)


if __name__ == "__main__":
    main()