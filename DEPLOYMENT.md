# StealthOCR Deployment Guide

This guide covers deploying StealthOCR to AWS Lambda and GitHub Pages.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.9+
- Node.js (for GitHub Pages deployment)
- Git

## AWS Lambda Deployment

### 1. Deploy Lambda Function

```bash
# Make deployment script executable
chmod +x lambda_deploy.sh

# Deploy to AWS (replace 'dev' with your environment)
./lambda_deploy.sh dev
```

The script will:
- Create a deployment package
- Deploy to AWS Lambda
- Create API Gateway
- Set up CORS
- Return the API endpoint URL

### 2. Update Frontend Configuration

After deployment, update `config.js` with your Lambda API endpoint:

```javascript
const CONFIG = {
    LAMBDA_API_URL: 'https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/ocr',
    // ... other config
};
```

### 3. Test Lambda Function

```bash
# Test with the provided PDF
python test_pdf_processing.py
```

## GitHub Pages Deployment

### 1. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages" section
3. Select "Deploy from a branch"
4. Choose "main" branch
5. Select "/ (root)" folder

### 2. Update API Configuration

Update `config.js` to use the Lambda API:

```javascript
const CONFIG = {
    LAMBDA_API_URL: 'https://your-lambda-api-url.amazonaws.com/prod/ocr',
    // ... other config
};
```

### 3. Deploy

```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

Your app will be available at: `https://syzygyx.github.io/StealthOCR`

## Local Development

### 1. Start Local Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask API server
python api_server.py
```

### 2. Open Frontend

Open `index.html` in your browser or serve it locally:

```bash
python -m http.server 8000
```

Then visit: `http://localhost:8000`

## Testing

### Test PDF Processing

```bash
# Test with provided PDF
python test_pdf_processing.py

# Test specific PDF
python extract_pdf_to_csv.py /path/to/your/pdf.pdf
```

### Test Web Interface

1. Open the web interface
2. Upload a PDF file
3. Check the extracted text
4. Download results

## Configuration

### Environment Variables

Set these in your Lambda function:

- `TESSDATA_PREFIX`: Path to Tesseract data files
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

### Lambda Settings

- **Memory**: 3008 MB (recommended)
- **Timeout**: 300 seconds (5 minutes)
- **Runtime**: Python 3.9

### API Gateway Settings

- **CORS**: Enabled for all origins
- **Request timeout**: 30 seconds
- **Integration timeout**: 300 seconds

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **No text extracted**: Check PDF quality and try different OCR engines
3. **Lambda timeout**: Increase memory or timeout settings
4. **CORS errors**: Check API Gateway CORS configuration

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. **Use higher DPI**: Increase DPI for better OCR accuracy
2. **Preprocess images**: Apply image enhancement before OCR
3. **Use GPU**: Enable GPU acceleration for EasyOCR
4. **Batch processing**: Process multiple pages in parallel

## Security Considerations

1. **File size limits**: Implement client-side file size validation
2. **Rate limiting**: Add API Gateway throttling
3. **Authentication**: Add API keys or authentication if needed
4. **Input validation**: Validate PDF files before processing

## Monitoring

### CloudWatch Logs

Monitor Lambda execution logs in AWS CloudWatch.

### Metrics

Track:
- Invocation count
- Duration
- Error rate
- Memory usage

### Alarms

Set up CloudWatch alarms for:
- High error rate
- Long duration
- Memory usage

## Cost Optimization

1. **Provisioned concurrency**: For consistent usage
2. **Reserved capacity**: For predictable workloads
3. **S3 for large files**: Use S3 for files > 6MB
4. **Image optimization**: Reduce image size before processing

## Support

For issues and questions:
1. Check the logs
2. Review this documentation
3. Test with the provided PDF file
4. Create an issue in the repository