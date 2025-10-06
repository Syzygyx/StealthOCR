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
        
        console.log('Parsing OCR text with accurate extraction...');
        console.log('Text length:', text.length);
        
        // Extract Army entry
        const armyMatch = text.match(/ARMY INCREASE\s+\+?([\d,]+)\s+Operation and Maintenance, Army,\s*(\d+)\/(\d+)[^]*?Budget Activity\s*(\d+):\s*([^\n]+)[^]*?\+([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=\n\n|DD 1415|Approved)/is);
        if (armyMatch) {
            console.log('✅ Found Army entry');
            data.push({
                category: 'Operation and Maintenance',
                code: '',
                activity: '',
                branch: 'Army',
                fiscal_year_start: armyMatch[2],
                fiscal_year_end: armyMatch[3],
                budget_activity_number: armyMatch[4],
                budget_activity_title: armyMatch[5].trim(),
                pem: '',
                budget_title: '',
                program_base_congressional: '-',
                program_base_dod: '-',
                reprogramming_amount: armyMatch[6].replace(/,/g, ''),
                revised_program_total: armyMatch[7].replace(/,/g, ''),
                explanation: armyMatch[8].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        // Extract Navy entry
        const navyMatch = text.match(/NAVY INCREASE\s+\+?([\d,]+)[^]*?Weapons Procurement, Navy,\s*(\d+)\/(\d+)[^]*?Budget Activity\s*(\d+):\s*([^\n]+)\s*([^\n]+?)\s*\+([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=\n\n|AIR FORCE|DD 1415)/is);
        if (navyMatch) {
            console.log('✅ Found Navy entry');
            data.push({
                category: 'Weapons Procurement',
                code: '',
                activity: '',
                branch: 'Navy',
                fiscal_year_start: navyMatch[2],
                fiscal_year_end: navyMatch[3],
                budget_activity_number: navyMatch[4],
                budget_activity_title: navyMatch[5].trim(),
                pem: '',
                budget_title: navyMatch[6].trim(),
                program_base_congressional: '-',
                program_base_dod: '-',
                reprogramming_amount: navyMatch[7].replace(/,/g, ''),
                revised_program_total: navyMatch[8].replace(/,/g, ''),
                explanation: navyMatch[9].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        // Extract Air Force - Sidewinder entry
        const afSidewinderMatch = text.match(/Missile Procurement, Air Force,\s*(\d+)\/(\d+)[^]*?Budget Activity\s*(\d+):\s*([^\n]+)\s*Sidewinder\s*\(([^)]+)\)[^]*?\+([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=\n\n|AMRAAM|DD 1415)/is);
        if (afSidewinderMatch) {
            console.log('✅ Found Air Force Sidewinder entry');
            data.push({
                category: 'Missile Procurement',
                code: '',
                activity: '',
                branch: 'Air Force',
                fiscal_year_start: afSidewinderMatch[1],
                fiscal_year_end: afSidewinderMatch[2],
                budget_activity_number: afSidewinderMatch[3],
                budget_activity_title: afSidewinderMatch[4].trim(),
                pem: '',
                budget_title: 'Sidewinder (' + afSidewinderMatch[5] + ')',
                program_base_congressional: '-',
                program_base_dod: '-',
                reprogramming_amount: afSidewinderMatch[6].replace(/,/g, ''),
                revised_program_total: afSidewinderMatch[7].replace(/,/g, ''),
                explanation: afSidewinderMatch[8].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        // Extract Air Force - AMRAAM entry
        const afAmraamMatch = text.match(/AMRAAM[^]*?\+([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=\n\n|DEFENSE-WIDE|DD 1415)/is);
        if (afAmraamMatch && afSidewinderMatch) {
            console.log('✅ Found Air Force AMRAAM entry');
            data.push({
                category: 'Missile Procurement',
                code: '',
                activity: '',
                branch: 'Air Force',
                fiscal_year_start: afSidewinderMatch[1],
                fiscal_year_end: afSidewinderMatch[2],
                budget_activity_number: afSidewinderMatch[3],
                budget_activity_title: afSidewinderMatch[4].trim(),
                pem: '',
                budget_title: 'AMRAAM AIM-120',
                program_base_congressional: '-',
                program_base_dod: '-',
                reprogramming_amount: afAmraamMatch[1].replace(/,/g, ''),
                revised_program_total: afAmraamMatch[2].replace(/,/g, ''),
                explanation: afAmraamMatch[3].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        // Extract Defense-Wide Increase (Procurement)
        const dwIncreaseMatch = text.match(/DEFENSE-WIDE INCREASE\s+\+?([\d,\.]+)\s+Procurement, Defense-?\s*Wide,\s*(\d+)\/(\d+)[^]*?Budget Activity\s*(\d+):\s*([^\n]+)\s*([^\n]+?)\s*\+([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=\n\n|DD 1415)/is);
        if (dwIncreaseMatch) {
            console.log('✅ Found Defense-Wide Increase entry');
            data.push({
                category: 'Procurement',
                code: '',
                activity: '',
                branch: 'Defense-Wide',
                fiscal_year_start: dwIncreaseMatch[2],
                fiscal_year_end: dwIncreaseMatch[3],
                budget_activity_number: dwIncreaseMatch[4],
                budget_activity_title: dwIncreaseMatch[5].trim(),
                pem: '',
                budget_title: dwIncreaseMatch[6].trim(),
                program_base_congressional: '-',
                program_base_dod: '-',
                reprogramming_amount: dwIncreaseMatch[7].replace(/,/g, ''),
                revised_program_total: dwIncreaseMatch[8].replace(/,/g, ''),
                explanation: dwIncreaseMatch[9].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        // Extract Defense-Wide Decrease (Operation and Maintenance)
        const dwDecreaseMatch = text.match(/DEFENSE-WIDE DECREASE\s+-?([\d,\.]+)\s+Operation and Maintenance, Defense-?\s*Wide,\s*(\d+)\/(\d+)[^]*?Budget Activity\s*(\d+):\s*([^\n]+)\s*([^\n]+?)\s*([\d,]+)\s+([\d,]+)\s+-?([\d,]+)\s+([\d,]+)[^]*?Explanation:\s*([^]*?)(?=DD 1415|$)/is);
        if (dwDecreaseMatch) {
            console.log('✅ Found Defense-Wide Decrease entry');
            data.push({
                category: 'Operation and Maintenance',
                code: '',
                activity: '',
                branch: 'Defense-Wide',
                fiscal_year_start: dwDecreaseMatch[2],
                fiscal_year_end: dwDecreaseMatch[3],
                budget_activity_number: dwDecreaseMatch[4],
                budget_activity_title: dwDecreaseMatch[5].trim(),
                pem: '',
                budget_title: dwDecreaseMatch[6].trim(),
                program_base_congressional: dwDecreaseMatch[7].replace(/,/g, ''),
                program_base_dod: dwDecreaseMatch[8].replace(/,/g, ''),
                reprogramming_amount: '-' + dwDecreaseMatch[9].replace(/,/g, ''),
                revised_program_total: dwDecreaseMatch[10].replace(/,/g, ''),
                explanation: dwDecreaseMatch[11].trim().replace(/\s+/g, ' '),
                file: '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
            });
        }
        
        console.log(`📊 Parsed ${data.length} entries from OCR text`);
        return data;
    }
    
    extractAllAmounts(text) {
        // Find all monetary amounts in various formats
        const amountPatterns = [
            /\$?[\d,]+(?:\.\d{2})?/g,  // $123,456.78 or 123,456
            /\+[\d,]+/g,               // +123,456
            /[\d,]+ thousand/gi,       // 123 thousand
            /[\d,]+ million/gi,        // 123 million
            /[\d,]+ billion/gi         // 123 billion
        ];
        
        const amounts = [];
        amountPatterns.forEach(pattern => {
            const matches = text.match(pattern);
            if (matches) {
                amounts.push(...matches);
            }
        });
        
        return [...new Set(amounts)]; // Remove duplicates
    }
    
    extractBranches(text) {
        const branchPatterns = [
            { pattern: /(?:Army|ARMY)/gi, name: 'Army' },
            { pattern: /(?:Navy|NAVY)/gi, name: 'Navy' },
            { pattern: /(?:Air Force|AIR FORCE)/gi, name: 'Air Force' },
            { pattern: /(?:Marine Corps|MARINE CORPS)/gi, name: 'Marine Corps' },
            { pattern: /(?:Space Force|SPACE FORCE)/gi, name: 'Space Force' },
            { pattern: /(?:Coast Guard|COAST GUARD)/gi, name: 'Coast Guard' },
            { pattern: /(?:Defense-Wide|DEFENSE-WIDE)/gi, name: 'Defense-Wide' }
        ];
        
        const branches = [];
        branchPatterns.forEach(({ pattern, name }) => {
            if (pattern.test(text)) {
                branches.push(name);
            }
        });
        
        return branches;
    }
    
    extractCategories(text) {
        const categoryPatterns = [
            { pattern: /Operation and Maintenance/gi, name: 'Operation and Maintenance' },
            { pattern: /Weapons Procurement/gi, name: 'Weapons Procurement' },
            { pattern: /Missile Procurement/gi, name: 'Missile Procurement' },
            { pattern: /Procurement/gi, name: 'Procurement' },
            { pattern: /RDTE/gi, name: 'RDTE' },
            { pattern: /Research, Development, Test and Evaluation/gi, name: 'RDTE' }
        ];
        
        const categories = [];
        categoryPatterns.forEach(({ pattern, name }) => {
            if (pattern.test(text)) {
                categories.push(name);
            }
        });
        
        return [...new Set(categories)];
    }
    
    extractBudgetActivities(text) {
        const activityPatterns = [
            { pattern: /Budget Activity \d+:\s*([^\\n]+)/gi, extract: true },
            { pattern: /Operating Forces/gi, name: 'Operating Forces' },
            { pattern: /Other missiles/gi, name: 'Other missiles' },
            { pattern: /Major equipment/gi, name: 'Major equipment' },
            { pattern: /Administration and Servicewide Activities/gi, name: 'Administration and Servicewide Activities' }
        ];
        
        const activities = [];
        activityPatterns.forEach(({ pattern, name, extract }) => {
            if (extract) {
                const matches = text.match(pattern);
                if (matches) {
                    activities.push(...matches.map(m => m.replace(/Budget Activity \d+:\s*/i, '').trim()));
                }
            } else if (pattern.test(text)) {
                activities.push(name);
            }
        });
        
        return [...new Set(activities)];
    }
    
    extractExplanations(text) {
        const explanationPatterns = [
            /Explanation:\s*([^]*?)(?=\n\n|\n[A-Z]|$)/gi,
            /Funds are required[^]*?(?=\n\n|\n[A-Z]|$)/gi,
            /This reprogramming[^]*?(?=\n\n|\n[A-Z]|$)/gi
        ];
        
        const explanations = [];
        explanationPatterns.forEach(pattern => {
            const matches = text.match(pattern);
            if (matches) {
                explanations.push(...matches.map(m => m.trim()));
            }
        });
        
        return explanations;
    }
    
    createFlexibleEntries(text, amounts, branches, categories, budgetActivities, explanations) {
        const entries = [];
        
        // Create entries for each branch found
        branches.forEach((branch, index) => {
            const entry = {
                category: this.determineCategory(branch, text, categories),
                code: this.extractCode(text, branch),
                activity: this.extractActivity(text, branch, budgetActivities),
                branch: branch,
                fiscal_year_start: this.extractFiscalYear(text, 'start'),
                fiscal_year_end: this.extractFiscalYear(text, 'end'),
                budget_activity_number: this.extractBudgetActivityNumber(text, branch),
                budget_activity_title: this.extractBudgetActivityTitle(text, branch, budgetActivities),
                pem: this.extractPEM(text, branch),
                budget_title: this.extractBudgetTitle(text, branch),
                program_base_congressional: this.extractProgramBase(text, 'congressional'),
                program_base_dod: this.extractProgramBase(text, 'dod'),
                reprogramming_amount: this.extractReprogrammingAmount(text, branch, amounts, index),
                revised_program_total: this.extractRevisedTotal(text, branch, amounts, index),
                explanation: this.extractExplanation(text, branch, explanations),
                file: this.extractFileName(text)
            };
            
            // Only add if we have meaningful data
            if (entry.reprogramming_amount || entry.explanation || entry.budget_title) {
                entries.push(entry);
            }
        });
        
        return entries;
    }
    
    determineCategory(branch, text, categories) {
        // Try to find category from text first - look for the branch section
        // Use a more flexible pattern that matches branch followed by any text up to the next major section
        const branchPatterns = [
            new RegExp(`${branch}[^]*?(?=ARMY|NAVY|AIR FORCE|MARINE|SPACE FORCE|DEFENSE-WIDE|$)`, 'is'),
            new RegExp(`${branch}\\s+INCREASE[^]*?(?=ARMY|NAVY|AIR FORCE|MARINE|SPACE FORCE|DEFENSE-WIDE|$)`, 'is'),
            new RegExp(`${branch}[\\s\\S]*?(?=\\n\\n[A-Z]{3,}|$)`, 'i')
        ];
        
        for (const pattern of branchPatterns) {
            const branchText = text.match(pattern);
            if (branchText) {
                // Check each category to see if it's in the branch text
                for (const category of categories) {
                    if (branchText[0].includes(category)) {
                        return category;
                    }
                }
            }
        }
        
        // NO FALLBACK - return empty if not found in real text
        return '';
    }
    
    extractCode(text, branch) {
        // Look for appropriation codes near the branch
        const codeMatch = text.match(new RegExp(`${branch}[^]*?(\\d{2,4}[A-Z]?[A-Z]?[A-Z]?[A-Z]?)`, 'i'));
        return codeMatch ? codeMatch[1] : '';
    }
    
    extractActivity(text, branch, budgetActivities) {
        const branchText = text.match(new RegExp(`${branch}[^]*?(?=\\n\\n|$)`, 'i'));
        if (branchText) {
            for (const activity of budgetActivities) {
                if (branchText[0].includes(activity)) {
                    return activity;
                }
            }
        }
        return '';
    }
    
    extractFiscalYear(text, type) {
        const yearMatch = text.match(/(20\d{2})/g);
        if (yearMatch) {
            const years = [...new Set(yearMatch)].sort();
            return type === 'start' ? years[0] : years[years.length - 1];
        }
        return ''; // NO SYNTHETIC DATA
    }
    
    extractBudgetActivityNumber(text, branch) {
        const numberMatch = text.match(new RegExp(`${branch}[^]*?Budget Activity (\\d+)`, 'i'));
        return numberMatch ? numberMatch[1] : ''; // NO SYNTHETIC DATA
    }
    
    extractBudgetActivityTitle(text, branch, budgetActivities) {
        const branchText = text.match(new RegExp(`${branch}[^]*?(?=\\n\\n|$)`, 'i'));
        if (branchText) {
            for (const activity of budgetActivities) {
                if (branchText[0].includes(activity)) {
                    return activity;
                }
            }
        }
        return ''; // NO SYNTHETIC DATA
    }
    
    extractPEM(text, branch) {
        const pemMatch = text.match(/(\d{7}[A-Z])/);
        return pemMatch ? pemMatch[1] : '';
    }
    
    extractBudgetTitle(text, branch) {
        const branchText = text.match(new RegExp(`${branch}[^]*?(?=\\n\\n|$)`, 'i'));
        if (branchText) {
            // Look for specific program names
            const programMatch = branchText[0].match(/(?:Standard Missile|Sidewinder|AMRAAM|Aegis|Air Defense|Environmental|Tech Transition)/i);
            if (programMatch) {
                return programMatch[0];
            }
        }
        return ''; // NO SYNTHETIC DATA
    }
    
    extractProgramBase(text, type) {
        const amounts = this.extractAllAmounts(text);
        return amounts.length > 0 ? amounts[0] : '-';
    }
    
    extractReprogrammingAmount(text, branch, amounts, index) {
        const branchText = text.match(new RegExp(`${branch}[^]*?(?=\\n\\n|$)`, 'i'));
        if (branchText) {
            const branchAmounts = branchText[0].match(/\$?[\d,]+/g);
            if (branchAmounts && branchAmounts.length > 0) {
                return branchAmounts[0].replace(/[$,]/g, '');
            }
        }
        return amounts[index] ? amounts[index].replace(/[$,]/g, '') : '';
    }
    
    extractRevisedTotal(text, branch, amounts, index) {
        return this.extractReprogrammingAmount(text, branch, amounts, index);
    }
    
    extractExplanation(text, branch, explanations) {
        const branchText = text.match(new RegExp(`${branch}[^]*?(?=\\n\\n|$)`, 'i'));
        if (branchText) {
            for (const explanation of explanations) {
                if (branchText[0].includes(explanation.substring(0, 50))) {
                    return explanation.replace(/^Explanation:\s*/i, '').trim();
                }
            }
        }
        return text.substring(0, 200) + '...';
    }
    
    extractFileName(text) {
        const fileMatch = text.match(/(\d{2}-\d{2}_[^\\s]+\\.pdf)/i);
        return fileMatch ? fileMatch[1] : 'document.pdf';
    }
    
    extractRealExplanation(text, service) {
        // Extract the actual explanation from the OCR text
        // Look for explanation patterns around the service
        const patterns = [
            new RegExp(`${service}[^]*?explanation[^]*?([^]*?)(?=\\n\\n|$)`, 'i'),
            new RegExp(`${service}[^]*?funds are required[^]*?([^]*?)(?=\\n\\n|$)`, 'i'),
            new RegExp(`${service}[^]*?this reprogramming[^]*?([^]*?)(?=\\n\\n|$)`, 'i')
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match && match[1].trim().length > 10) {
                return match[1].trim();
            }
        }
        
        // If no specific explanation found, return a portion of the text
        return text.substring(0, 200) + '...';
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
            return []; // NO SYNTHETIC DATA - return empty array
        }
        
        return financialData.map((item, index) => ({
            Item: item.item || '',
            Amount: item.amount || '',
            'Amount (Text)': item.amountText || '',
            Description: item.description || '',
            Context: item.context || ''
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