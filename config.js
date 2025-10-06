// StealthOCR Configuration
const CONFIG = {
    // Lambda API endpoint - update this after deployment
    LAMBDA_API_URL: 'https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/ocr',
    
    // Fallback to local API if Lambda is not available
    LOCAL_API_URL: '/api/ocr',
    
    // Default OCR engine
    DEFAULT_ENGINE: 'tesseract',
    
    // Maximum file size (in MB)
    MAX_FILE_SIZE: 10,
    
    // Supported file types
    SUPPORTED_TYPES: ['application/pdf'],
    
    // Processing timeout (in seconds)
    TIMEOUT: 300
};

// Auto-detect API endpoint
function getApiUrl() {
    // Check if we're running on GitHub Pages or local
    if (window.location.hostname === 'syzygyx.github.io' || 
        window.location.hostname.includes('github.io')) {
        // Use the deployed Lambda API
        return 'https://milk3i80mh.execute-api.us-east-1.amazonaws.com/prod/ocr';
    } else {
        return CONFIG.LOCAL_API_URL;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, getApiUrl };
}