#!/usr/bin/env node
/**
 * CLI test for JavaScript OCR and CSV parsing
 */

const fs = require('fs');
const path = require('path');

// Mock browser environment for Node.js
global.window = {
    location: { href: 'http://localhost:8080' }
};

global.document = {
    getElementById: () => ({ style: {}, innerHTML: '', textContent: '' }),
    createElement: () => ({ style: {}, innerHTML: '', textContent: '' }),
    head: { insertAdjacentHTML: () => {} }
};

global.console = console;

// Load the Excel display module
const excelDisplayPath = path.join(__dirname, 'js', 'excel-display.js');
const excelDisplayCode = fs.readFileSync(excelDisplayPath, 'utf8');

// Execute the Excel display code
eval(excelDisplayCode);

// Test with real OCR text from the PDF
const realOcrText = `ified REPROGRAMMING ACTION - INTERNAL REPROGRAMMING Page | of 3

Subject: Israel Security Replacement Transfer Fund Tranche 3
Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?

Yes

Component Serial Number: (Amounts in Thousands of Dollars)
Severe
Congressional Action Approved by Sec Def
ee
a

This reprogramming action provides funding for the replacement of defense articles from the stocks of the
Department of Defense expended in support of Israel and for the reimbursement of defense services of the
Department of Defense provided to Israel or identified and notified to Congress for provision to Israel. This
action is determined to be necessary in the national interest. This reprogramming action meets all

administrative and legal requirements, and none of the items have been previously denied by the Congress.

2

This reprogramming action transfers $657.584 million from the Operation and Maintenance, Defense-Wide,
24/25, appropmiation to various Defense appropriations pursuant to the funding appropriated in division A of
Public Law 118-50, the Israel Security Supplemental Appropriations Act, 2024.

The transfer authority provided with the replacement funding in Public Law 118-50 is in addition to any
other transfer authority available to the Department of Defense.

This reprogramming action addresses funds for the replacement of defense articles expended in support of
Israel through U.S. combat operations executed at the request of and in coordination with Israel and for the
defense of Israeli territory, personnel, or assets during the April 13, 2024, and October 1, 2024, attacks by

Iran and reimburses DoD direct support costs expended, in coordination with and at the request of Israel, in
order to defend against attacks on Israeli territory, personnel, or assets.

FY 2025 REPROGRAMMING INCREASES: +657,584

ARMY INCREASE +118,600

+118,600

Operation and Maintenance, Army, 25/25
Budget Activity 01: ting Forces

+118,600 118,600

Explanation: Funds are required for reimbursement for the deployment of air defense materiel, equipment,
and services directly provided or identified and notified to Congress through this reprogramming action for
provision to the Government of Israel. This is a congressional special interest item. This is an emergency

budget requirement.

pproved (Signature and Date)
Moe) Walz

DD 1415-3 UNCLASSIFIED
d REPROGRAMMING ACTION - INTERNAL REPROGRAMMING
ubject: Israel Security Replacement Transfer Fund Tranche 3 DoD Serial Number:

Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?

Yes

Component Serial Number: (Amounts in Thousands of Dollars)
"Coepranenl Acton
Congressional Action Approved by Sec Def
ee
a

NAVY INCREASE +105,252

Weapons Procurement, Navy, 25/27
Budget Activity 02: Other missiles

Standard Missile

ay
ba'
a
S

ll
my

+105,252

+105,252 105,252

Explanation: Funds are required for the replacement of Standard Missiles expended in support of Israel.
This is a congressional special interest item. This is an emergency budget requirement.

AIR FORCE INCREASE

Missile Procurement, Air Force, 25/27

Budget Activity 02: Other missiles
Sidewinder (AIM-9X)

+14,500 14,500

Explanation: Funds are required for the replacement of AIM-9X Sidewinder missiles expended in support of
Israel. This is a congressional special interest item. This is an emergency budget requirement.

AMRAAM

+62,982 62,982

Explanation: Funds are required for the replacement of AMRAAM AIM-120 missiles expended in support
of Israel. This is a congressional special interest item. This is an emergency budget requirement.

DEFENSE-WIDE INCREASE

Procurement, Defense- Wide, 25/27

Budget Activity 01: Major equipment
Aegis BMD

+356,250

+356,250

+356,250 356,250

Explanation: Funds are required for the replacement Standard Missile (SM)- 3 Block IB Threat Upgrade
(TU) All-up Rounds (AURs) and associated canisters expended in support of Israel. This is a congressional
special interest item. This is an emergency budget requirement.

DD 1415-3 UNCLASSIFIED
ied REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

iff dof}
Subject: Israel Security Replacement Transfer Fund Tranche 3 DoD Serial Number:

Appropriation Title: Various Appropriations FY 25-08 IR
Includes Transfer?

Yes

Component Serial Number: (Amounts in Thousands of Dollars)
Program Base Reflecting Program Previously Reprogramming Action Revised Program
i Approved by Sec Def

Congressional Action
a SO

FY 2025 REPROGRAMMING DECREASE: 657.5:

i

DEFENSE-WIDE DECREASE

Operation and Maintenance, Defense-Wide, 24/25 -657,584
Budget Activity 04: Administration and Servicewide Activities
Israel Replacement Transfer Fund
4,400,000 3,175,117 -657,584 2,517,533

Explanation: Funds are available from division A of Israel Security Supplemental Appropriations Act, 2024,
division A of Public Law 118-50, appropriated to the Department of Defense and made available for transfer
to respond to the situation in Israel, and for replacement, through new procurement or repair of existing
unserviceable equipment, of defense articles from the stocks of the Department of Defense, and for
reimbursement for defense services of the Department of Defense and military education and training,
provided to the government of Israel or identified and notified to Congress for provision to the goverment
of Israel or to foreign countries that have provided support to Israel at the request of the United States.

DD 1415-3 UNCLASSIFIED`;

async function testCLI() {
    console.log('🧪 Testing JavaScript OCR and CSV parsing via CLI...\n');
    
    try {
        // Create an instance of the ExcelDisplay class
        const excelDisplay = new ExcelDisplay();
        
        console.log('📄 Processing real OCR text...');
        console.log(`Text length: ${realOcrText.length} characters\n`);
        
        // Test CSV generation
        console.log('🔄 Generating CSV from real OCR text...');
        const csvData = excelDisplay.generateCSVFromOCR(realOcrText);
        
        console.log('📊 Generated CSV:');
        console.log('='.repeat(80));
        console.log(csvData);
        console.log('='.repeat(80));
        
        // Save results
        const outputFile = 'cli_test_output.csv';
        fs.writeFileSync(outputFile, csvData);
        console.log(`\n💾 CSV saved to ${outputFile}`);
        
        // Show summary
        const lines = csvData.split('\n');
        console.log(`\n📈 Summary:`);
        console.log(`- Header row: 1`);
        console.log(`- Data rows: ${lines.length - 1}`);
        console.log(`- Total lines: ${lines.length}`);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        console.error(error.stack);
    }
}

// Run the test
testCLI();