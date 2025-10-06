/**
 * Excel Display Library for StealthOCR
 * Handles Excel file generation and display in the browser
 */

class ExcelDisplay {
    constructor() {
        this.sheetJSLoaded = false;
        this.loadSheetJS();
    }

    async loadSheetJS() {
        if (this.sheetJSLoaded) return;
        
        try {
            // Load SheetJS from CDN
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
            script.onload = () => {
                this.sheetJSLoaded = true;
                console.log('SheetJS loaded successfully');
            };
            document.head.appendChild(script);
        } catch (error) {
            console.error('Failed to load SheetJS:', error);
        }
    }

    async generateCSVFromOCR(ocrData) {
        // Generate CSV data in the exact format required
        const csvData = this.createExactCSVData(ocrData);
        return csvData;
    }

    createExactCSVData(ocrData) {
        const text = ocrData.text || '';
        
        // Parse the OCR text to extract appropriation data
        const appropriationData = this.parseAppropriationData(text);
        
        // Create CSV rows
        const csvRows = [];
        
        // Add header row
        csvRows.push([
            'appropriation_category',
            'appropriation code',
            'appropriation activity',
            'branch',
            'fiscal_year_start',
            'fiscal_year_end',
            'budget_activity_number',
            'budget_activity_title',
            'pem',
            'budget_title',
            'program_base_congressional',
            'program_base_dod',
            'reprogramming_amount',
            'revised_program_total',
            'explanation',
            'file'
        ]);
        
        // Add data rows
        appropriationData.forEach(row => {
            csvRows.push([
                row.category || '',
                row.code || '',
                row.activity || '',
                row.branch || '',
                row.fiscal_year_start || '2025',
                row.fiscal_year_end || '2025',
                row.budget_activity_number || '',
                row.budget_activity_title || '',
                row.pem || '',
                row.budget_title || '',
                row.program_base_congressional || '',
                row.program_base_dod || '',
                row.reprogramming_amount || '',
                row.revised_program_total || '',
                row.explanation || '',
                row.file || ''
            ]);
        });
        
        return csvRows;
    }

    parseAppropriationData(text) {
        const data = [];
        
        // Look for ARMY INCREASE
        const armyMatch = text.match(/ARMY INCREASE[^]*?Explanation:\s*([^]*?)(?=NAVY INCREASE|AIR FORCE INCREASE|DEFENSE-WIDE INCREASE|$)/i);
        if (armyMatch) {
            data.push({
                category: 'Operation and Maintenance',
                branch: 'Army',
                reprogramming_amount: this.extractAmount(text, /ARMY INCREASE[^]*?\+([\d,]+)/i),
                explanation: armyMatch[1].trim()
            });
        }
        
        // Look for NAVY INCREASE
        const navyMatch = text.match(/NAVY INCREASE[^]*?Explanation:\s*([^]*?)(?=AIR FORCE INCREASE|DEFENSE-WIDE INCREASE|$)/i);
        if (navyMatch) {
            data.push({
                category: 'Weapons Procurement',
                branch: 'Navy',
                reprogramming_amount: this.extractAmount(text, /NAVY INCREASE[^]*?\+([\d,]+)/i),
                explanation: navyMatch[1].trim()
            });
        }
        
        // Look for AIR FORCE INCREASE
        const airForceMatch = text.match(/AIR FORCE INCREASE[^]*?Explanation:\s*([^]*?)(?=DEFENSE-WIDE INCREASE|$)/i);
        if (airForceMatch) {
            data.push({
                category: 'Missile Procurement',
                branch: 'Air Force',
                reprogramming_amount: this.extractAmount(text, /AIR FORCE INCREASE[^]*?\+([\d,]+)/i),
                explanation: airForceMatch[1].trim()
            });
        }
        
        // Look for DEFENSE-WIDE INCREASE
        const defenseWideMatch = text.match(/DEFENSE-WIDE INCREASE[^]*?Explanation:\s*([^]*?)(?=DEFENSE-WIDE DECREASE|$)/i);
        if (defenseWideMatch) {
            data.push({
                category: 'Procurement',
                branch: 'Defense-Wide',
                reprogramming_amount: this.extractAmount(text, /DEFENSE-WIDE INCREASE[^]*?\+([\d,]+)/i),
                explanation: defenseWideMatch[1].trim()
            });
        }
        
        // Look for DEFENSE-WIDE DECREASE
        const decreaseMatch = text.match(/DEFENSE-WIDE DECREASE[^]*?Explanation:\s*([^]*?)$/i);
        if (decreaseMatch) {
            data.push({
                category: 'Operation and Maintenance',
                branch: 'Defense-Wide',
                reprogramming_amount: '-' + this.extractAmount(text, /DEFENSE-WIDE DECREASE[^]*?-([\d,]+)/i),
                explanation: decreaseMatch[1].trim()
            });
        }
        
        return data;
    }

    extractAmount(text, pattern) {
        const match = text.match(pattern);
        return match ? match[1] : '';
    }

    createSummaryData(ocrData) {
        const metadata = this.extractMetadata(ocrData.text);
        const financialData = this.extractFinancialData(ocrData.text);
        
        return [
            { Field: 'Document Title', Value: metadata.documentTitle || 'N/A' },
            { Field: 'Serial Number', Value: metadata.serialNumber || 'N/A' },
            { Field: 'Appropriation Title', Value: metadata.appropriationTitle || 'N/A' },
            { Field: 'Includes Transfer', Value: metadata.includesTransfer || 'N/A' },
            { Field: 'Component Serial', Value: metadata.componentSerial || 'N/A' },
            { Field: 'Total Financial Items', Value: financialData.length },
            { Field: 'Total Amount', Value: this.calculateTotalAmount(financialData) },
            { Field: 'Extraction Date', Value: new Date().toLocaleString() },
            { Field: 'Document Type', Value: 'Reprogramming Action' },
            { Field: 'Pages Processed', Value: ocrData.pages_processed || 0 },
            { Field: 'Characters Extracted', Value: ocrData.character_count || 0 },
            { Field: 'Words Extracted', Value: ocrData.word_count || 0 }
        ];
    }

    createFinancialData(ocrData) {
        const financialData = this.extractFinancialData(ocrData.text);
        
        if (financialData.length === 0) {
            return [{ Item: 'No financial data found', Amount: 0, Description: 'N/A' }];
        }
        
        return financialData.map((item, index) => ({
            Item: item.item || `Financial Item ${index + 1}`,
            Amount: item.amount || 0,
            'Amount (Text)': item.amountText || '$0',
            Description: item.description || 'N/A',
            Context: item.context || 'N/A'
        }));
    }

    createProgramData(ocrData) {
        const programDetails = this.extractProgramDetails(ocrData.text);
        
        return [
            { Category: 'Narrative', Description: programDetails.narrative || 'N/A' },
            { Category: 'National Interest', Description: programDetails.nationalInterest ? 'Yes' : 'No' },
            { Category: 'Legal Requirements', Description: programDetails.meetsLegalRequirements ? 'Yes' : 'No' },
            { Category: 'Description', Description: programDetails.description || 'N/A' }
        ];
    }

    createRawTextData(ocrData) {
        const text = ocrData.text || '';
        const chunks = [];
        const chunkSize = 1000;
        
        for (let i = 0; i < text.length; i += chunkSize) {
            chunks.push({
                Chunk: Math.floor(i / chunkSize) + 1,
                Text: text.substring(i, i + chunkSize)
            });
        }
        
        return chunks;
    }

    extractMetadata(text) {
        const patterns = {
            documentTitle: /(?:Subject|Title):\s*(.+?)(?:\n|$)/i,
            serialNumber: /(?:DoD Serial Number|Serial Number):\s*(.+?)(?:\n|$)/i,
            appropriationTitle: /(?:Appropriation Title):\s*(.+?)(?:\n|$)/i,
            includesTransfer: /(?:Includes Transfer\?)\s*(Yes|No)/i,
            componentSerial: /(?:Component Serial Number):\s*(.+?)(?:\n|$)/i
        };
        
        const metadata = {};
        
        for (const [key, pattern] of Object.entries(patterns)) {
            const match = text.match(pattern);
            if (match) {
                metadata[key] = match[1].trim();
            }
        }
        
        return metadata;
    }

    extractFinancialData(text) {
        const financialData = [];
        
        // Look for funding amounts
        const fundingPattern = /(?:transfers?|funding)\s*\$?([\d,]+)/gi;
        let match;
        let index = 1;
        
        while ((match = fundingPattern.exec(text)) !== null) {
            const amount = match[1].replace(/,/g, '');
            const amountValue = parseFloat(amount) || 0;
            
            financialData.push({
                item: `Funding Item ${index}`,
                amount: amountValue,
                amountText: `$${amountValue.toLocaleString()}`,
                description: 'Reprogramming action funding',
                context: match[0]
            });
            index++;
        }
        
        // Look for table data
        const tablePattern = /(Program Base|Congressional Action|Reprogramming Action|Revised Program)/gi;
        while ((match = tablePattern.exec(text)) !== null) {
            financialData.push({
                item: match[1],
                amount: 0,
                amountText: 'TBD',
                description: 'Program component',
                context: match[0]
            });
        }
        
        return financialData;
    }

    extractProgramDetails(text) {
        const details = {};
        
        // Extract narrative
        const narrativeMatch = text.match(/(?:This reprogramming action provides funding for|This action provides|The action provides)(.+?)(?:This action is determined|This reprogramming action meets|$)/is);
        if (narrativeMatch) {
            details.narrative = narrativeMatch[1].trim();
        }
        
        // Check for national interest
        details.nationalInterest = /necessary in the national interest/i.test(text);
        
        // Check for legal requirements
        details.meetsLegalRequirements = /meets all administrative and legal requirements/i.test(text);
        
        // Extract description
        const descMatch = text.match(/(?:This reprogramming action provides funding for|This action provides|The action provides)(.+?)(?:\.|$)/is);
        if (descMatch) {
            details.description = descMatch[1].trim();
        }
        
        return details;
    }

    calculateTotalAmount(financialData) {
        return financialData.reduce((total, item) => total + (item.amount || 0), 0);
    }

    async waitForSheetJS() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (this.sheetJSLoaded) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
        });
    }

    downloadExcel(workbook, filename = 'stealth_ocr_output.xlsx') {
        XLSX.writeFile(workbook, filename);
    }

    displayCSVPreview(csvData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create table for CSV data
        const table = document.createElement('table');
        table.className = 'csv-table';
        
        // Add header row
        const headerRow = document.createElement('tr');
        csvData[0].forEach(cell => {
            const th = document.createElement('th');
            th.textContent = cell;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
        
        // Add data rows
        for (let i = 1; i < csvData.length; i++) {
            const row = document.createElement('tr');
            csvData[i].forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                row.appendChild(td);
            });
            table.appendChild(row);
        }
        
        // Create table container
        const tableContainer = document.createElement('div');
        tableContainer.className = 'csv-container';
        tableContainer.appendChild(table);
        
        container.appendChild(tableContainer);
    }

    showSheet(workbook, sheetName, container, activeTab) {
        // Update active tab
        container.parentElement.querySelectorAll('.excel-tab').forEach(tab => tab.classList.remove('active'));
        activeTab.classList.add('active');
        
        // Convert sheet to HTML
        const worksheet = workbook.Sheets[sheetName];
        const html = XLSX.utils.sheet_to_html(worksheet);
        
        container.innerHTML = `
            <div class="excel-sheet">
                <h4>${sheetName}</h4>
                <div class="excel-table-container">
                    ${html}
                </div>
            </div>
        `;
    }
}

// CSS for Excel display
const excelStyles = `
<style>
.excel-tabs {
    display: flex;
    border-bottom: 2px solid #ddd;
    margin-bottom: 20px;
}

.excel-tab {
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-bottom: none;
    padding: 10px 20px;
    cursor: pointer;
    border-radius: 5px 5px 0 0;
    margin-right: 5px;
}

.excel-tab.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.excel-content {
    min-height: 400px;
}

.excel-sheet h4 {
    margin-bottom: 15px;
    color: #333;
}

.excel-table-container {
    overflow-x: auto;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.excel-table-container table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.excel-table-container th,
.excel-table-container td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}

.excel-table-container th {
    background-color: #f8f9fa;
    font-weight: bold;
}

.excel-table-container tr:nth-child(even) {
    background-color: #f9f9f9;
}

.excel-table-container tr:hover {
    background-color: #f0f0f0;
}

.excel-download-btn {
    background: #28a745;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin: 10px 0;
    font-size: 14px;
}

.excel-download-btn:hover {
    background: #218838;
}
</style>
`;

// Add styles to document
if (typeof document !== 'undefined') {
    document.head.insertAdjacentHTML('beforeend', excelStyles);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExcelDisplay;
}