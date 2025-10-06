#!/usr/bin/env node
/**
 * Test JavaScript OCR and CSV parsing using Node.js
 */

const fs = require('fs');
const path = require('path');

// Mock the browser environment for Node.js
global.window = {
    location: {
        href: 'http://localhost:8080'
    }
};

global.document = {
    getElementById: (id) => {
        console.log(`Mock document.getElementById('${id}')`);
        return {
            style: { display: 'block' },
            innerHTML: '',
            textContent: '',
            appendChild: (child) => console.log(`Mock appendChild for ${id}`),
            removeChild: (child) => console.log(`Mock removeChild for ${id}`)
        };
    },
    createElement: (tag) => {
        console.log(`Mock document.createElement('${tag}')`);
        return {
            style: {},
            innerHTML: '',
            textContent: '',
            appendChild: (child) => console.log(`Mock appendChild for ${tag}`),
            removeChild: (child) => console.log(`Mock removeChild for ${tag}`)
        };
    }
};

global.console = console;

// Load the Excel display module
const excelDisplayPath = path.join(__dirname, 'js', 'excel-display.js');
const excelDisplayCode = fs.readFileSync(excelDisplayPath, 'utf8');

// Mock PDF.js and Tesseract.js
global.PDFJS = {
    getDocument: (url) => {
        console.log(`Mock PDFJS.getDocument('${url}')`);
        return Promise.resolve({
            numPages: 1,
            getPage: (pageNum) => {
                console.log(`Mock PDFJS.getPage(${pageNum})`);
                return Promise.resolve({
                    render: (options) => {
                        console.log(`Mock PDFJS.render with canvas`);
                        return Promise.resolve({
                            promise: Promise.resolve()
                        });
                    },
                    getViewport: () => ({
                        width: 800,
                        height: 600
                    })
                });
            }
        });
    }
};

global.Tesseract = {
    recognize: (canvas, lang) => {
        console.log(`Mock Tesseract.recognize with language: ${lang}`);
        return Promise.resolve({
            data: {
                text: `REPROGRAMMING ACTION

Subject: Israel Security Replacement Transfer Fund Tranche 3

This reprogramming action transfers funds to support Israel Security Replacement Transfer Fund.

Army: $118,600 for Operation and Maintenance
Navy: $105,252 for Weapons Procurement  
Air Force: $30,000 for RDTE

Funds are required to fully fund the gross weapon system cost and support operations.`
            }
        });
    }
};

// Mock canvas
global.HTMLCanvasElement = function() {
    this.width = 800;
    this.height = 600;
    this.getContext = () => ({
        drawImage: () => console.log('Mock canvas drawImage'),
        clearRect: () => console.log('Mock canvas clearRect')
    });
};

// Execute the Excel display code
eval(excelDisplayCode);

// Test the CSV parsing
async function testCSVParsing() {
    console.log('🧪 Testing JavaScript OCR and CSV parsing...\n');
    
    try {
        // Create an instance of the ExcelDisplay class
        const excelDisplay = new ExcelDisplay();
        
        // Test with sample OCR text
        const sampleText = `REPROGRAMMING ACTION

Subject: Israel Security Replacement Transfer Fund Tranche 3

This reprogramming action transfers funds to support Israel Security Replacement Transfer Fund.

Army: $118,600 for Operation and Maintenance
Navy: $105,252 for Weapons Procurement  
Air Force: $30,000 for RDTE

Funds are required to fully fund the gross weapon system cost and support operations.`;

        console.log('📄 Sample OCR text:');
        console.log(sampleText);
        console.log('\n' + '='.repeat(50) + '\n');
        
        // Test CSV generation
        console.log('🔄 Generating CSV from OCR text...');
        const csvData = excelDisplay.generateCSVFromOCR(sampleText);
        
        console.log('📊 Generated CSV:');
        console.log(csvData);
        console.log('\n' + '='.repeat(50) + '\n');
        
        // Test individual parsing functions
        console.log('🔍 Testing individual parsing functions...');
        
        const parsedData = excelDisplay.parseAppropriationData(sampleText);
        console.log('Parsed appropriation data:');
        console.log(JSON.stringify(parsedData, null, 2));
        
        // Test amount extraction
        const amounts = excelDisplay.extractAllAmounts(sampleText);
        console.log('\nExtracted amounts:');
        console.log(amounts);
        
        // Test branch extraction
        const branches = excelDisplay.extractBranches(sampleText);
        console.log('\nExtracted branches:');
        console.log(branches);
        
        // Save results to file
        const outputFile = 'test_js_ocr_output.txt';
        const output = `JavaScript OCR Test Results
========================

Sample Text:
${sampleText}

Generated CSV:
${csvData}

Parsed Data:
${JSON.stringify(parsedData, null, 2)}

Amounts:
${JSON.stringify(amounts, null, 2)}

Branches:
${JSON.stringify(branches, null, 2)}
`;
        
        fs.writeFileSync(outputFile, output);
        console.log(`\n💾 Results saved to ${outputFile}`);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        console.error(error.stack);
    }
}

// Run the test
testCSVParsing();