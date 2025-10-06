# StealthOCR

A powerful and stealthy Optical Character Recognition (OCR) toolkit built with Python, designed for high-accuracy text extraction from images and documents.

## Features

- **Multiple OCR Engines**: Support for Tesseract, EasyOCR, and OpenCV-based text detection
- **Image Preprocessing**: Advanced image enhancement and preprocessing capabilities
- **PDF Processing**: Extract text from PDF documents
- **Batch Processing**: Process multiple images/documents at once
- **Web Interface**: Flask and Streamlit web applications for easy interaction
- **Stealth Mode**: Optimized for discrete text extraction with minimal resource usage

## Installation

### Prerequisites

- Python 3.8+
- Tesseract OCR engine

#### Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Syzygyx/StealthOCR.git
cd StealthOCR
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic OCR

```python
from stealth_ocr import StealthOCR

# Initialize OCR engine
ocr = StealthOCR()

# Extract text from image
text = ocr.extract_text('path/to/image.jpg')
print(text)
```

### Batch Processing

```python
# Process multiple images
results = ocr.batch_process(['image1.jpg', 'image2.png', 'document.pdf'])
for file_path, extracted_text in results.items():
    print(f"{file_path}: {extracted_text[:100]}...")
```

### Web Interface

Start the Streamlit web app:
```bash
streamlit run app.py
```

Or start the Flask API:
```bash
python api.py
```

## Supported Formats

- **Images**: JPG, PNG, TIFF, BMP, GIF
- **Documents**: PDF
- **Text**: Plain text, structured data

## OCR Engines

1. **Tesseract**: High accuracy for printed text
2. **EasyOCR**: Multi-language support with deep learning
3. **OpenCV**: Fast text detection and extraction

## Configuration

Create a `.env` file for configuration:

```env
TESSERACT_PATH=/usr/local/bin/tesseract
DEFAULT_LANGUAGE=eng
OUTPUT_FORMAT=txt
BATCH_SIZE=10
```

## API Endpoints

### Flask API

- `POST /api/ocr` - Extract text from uploaded image
- `POST /api/batch` - Process multiple files
- `GET /api/status` - Check service status

### Example API Usage

```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/ocr
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Tesseract OCR engine
- EasyOCR library
- OpenCV community
- All contributors and users

## Support

For issues and questions, please open an issue on GitHub or contact the development team.