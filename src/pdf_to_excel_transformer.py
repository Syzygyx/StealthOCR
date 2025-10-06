"""
PDF OCR to Excel Transformer
Converts OCR extracted text from PDFs into structured Excel files
"""

import re
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToExcelTransformer:
    """
    Transforms OCR extracted text from PDFs into structured Excel files
    """
    
    def __init__(self):
        self.patterns = {
            'document_title': r'(?:Subject|Title):\s*(.+?)(?:\n|$)',
            'serial_number': r'(?:DoD Serial Number|Serial Number):\s*(.+?)(?:\n|$)',
            'appropriation_title': r'(?:Appropriation Title):\s*(.+?)(?:\n|$)',
            'transfer_question': r'(?:Includes Transfer\?)\s*(Yes|No)',
            'component_serial': r'(?:Component Serial Number):\s*(.+?)(?:\n|$)',
            'amounts_section': r'(?:Amounts in Thousands of Dollars)',
            'program_base': r'(?:Program Base)',
            'congressional_action': r'(?:Congressional Action)',
            'reprogramming_action': r'(?:Reprogramming Action)',
            'revised_program': r'(?:Revised Program)',
            'funding_amount': r'(?:transfers?|funding)\s*\$?([\d,]+)',
            'description': r'(?:This reprogramming action provides funding for|This action provides|The action provides)(.+?)(?:\.|$)',
            'national_interest': r'(?:necessary in the national interest)',
            'legal_requirements': r'(?:meets all administrative and legal requirements)',
            'page_break': r'=== PAGE \d+ ===',
        }
    
    def transform_ocr_to_excel(self, ocr_text: str, output_file: str = None) -> str:
        """
        Transform OCR text to Excel format
        
        Args:
            ocr_text: Raw OCR extracted text
            output_file: Output Excel file path (optional)
            
        Returns:
            Path to created Excel file
        """
        logger.info("Starting OCR to Excel transformation...")
        
        # Parse the OCR text
        parsed_data = self._parse_ocr_text(ocr_text)
        
        # Create Excel file
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"stealth_ocr_output_{timestamp}.xlsx"
        
        self._create_excel_file(parsed_data, output_file)
        
        logger.info(f"Excel file created: {output_file}")
        return output_file
    
    def _parse_ocr_text(self, text: str) -> Dict[str, Any]:
        """Parse OCR text and extract structured data"""
        logger.info("Parsing OCR text...")
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Extract document metadata
        metadata = self._extract_metadata(cleaned_text)
        
        # Extract financial data
        financial_data = self._extract_financial_data(cleaned_text)
        
        # Extract program details
        program_details = self._extract_program_details(cleaned_text)
        
        # Extract narrative text
        narrative = self._extract_narrative(cleaned_text)
        
        return {
            'metadata': metadata,
            'financial_data': financial_data,
            'program_details': program_details,
            'narrative': narrative,
            'raw_text': cleaned_text
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('0', 'O')  # In certain contexts
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract document metadata"""
        metadata = {}
        
        # Extract document title
        title_match = re.search(self.patterns['document_title'], text, re.IGNORECASE)
        if title_match:
            metadata['document_title'] = title_match.group(1).strip()
        
        # Extract serial number
        serial_match = re.search(self.patterns['serial_number'], text, re.IGNORECASE)
        if serial_match:
            metadata['serial_number'] = serial_match.group(1).strip()
        
        # Extract appropriation title
        appropriation_match = re.search(self.patterns['appropriation_title'], text, re.IGNORECASE)
        if appropriation_match:
            metadata['appropriation_title'] = appropriation_match.group(1).strip()
        
        # Extract transfer question
        transfer_match = re.search(self.patterns['transfer_question'], text, re.IGNORECASE)
        if transfer_match:
            metadata['includes_transfer'] = transfer_match.group(1).strip()
        
        # Extract component serial
        component_match = re.search(self.patterns['component_serial'], text, re.IGNORECASE)
        if component_match:
            metadata['component_serial'] = component_match.group(1).strip()
        
        return metadata
    
    def _extract_financial_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial data from the text"""
        financial_data = []
        
        # Look for funding amounts
        funding_matches = re.finditer(self.patterns['funding_amount'], text, re.IGNORECASE)
        for i, match in enumerate(funding_matches):
            amount = match.group(1).replace(',', '')
            try:
                amount_value = float(amount)
                financial_data.append({
                    'item': f'Funding Item {i+1}',
                    'amount': amount_value,
                    'amount_text': f'${amount_value:,.0f}',
                    'context': match.group(0)
                })
            except ValueError:
                logger.warning(f"Could not parse amount: {amount}")
        
        # Look for table data (if present)
        table_data = self._extract_table_data(text)
        financial_data.extend(table_data)
        
        return financial_data
    
    def _extract_table_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract tabular data from the text"""
        table_data = []
        
        # Look for amounts section
        amounts_section = re.search(self.patterns['amounts_section'], text, re.IGNORECASE)
        if amounts_section:
            # Extract text after amounts section
            start_pos = amounts_section.end()
            section_text = text[start_pos:start_pos + 1000]  # Next 1000 characters
            
            # Look for program-related data
            program_matches = re.finditer(r'(Program Base|Congressional Action|Reprogramming Action|Revised Program)', section_text, re.IGNORECASE)
            for match in program_matches:
                table_data.append({
                    'item': match.group(1),
                    'amount': 0,  # Placeholder
                    'amount_text': 'TBD',
                    'context': match.group(0)
                })
        
        return table_data
    
    def _extract_program_details(self, text: str) -> Dict[str, Any]:
        """Extract program-specific details"""
        details = {}
        
        # Check for national interest
        if re.search(self.patterns['national_interest'], text, re.IGNORECASE):
            details['national_interest'] = True
        
        # Check for legal requirements
        if re.search(self.patterns['legal_requirements'], text, re.IGNORECASE):
            details['meets_legal_requirements'] = True
        
        # Extract description
        desc_match = re.search(self.patterns['description'], text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            details['description'] = desc_match.group(1).strip()
        
        return details
    
    def _extract_narrative(self, text: str) -> str:
        """Extract the main narrative text"""
        # Find the main description paragraph
        desc_match = re.search(r'(?:This reprogramming action provides funding for|This action provides|The action provides)(.+?)(?:This action is determined|This reprogramming action meets|$)', text, re.IGNORECASE | re.DOTALL)
        
        if desc_match:
            return desc_match.group(1).strip()
        
        # Fallback: return first substantial paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 100:
                return para.strip()
        
        return text[:500] + "..." if len(text) > 500 else text
    
    def _create_excel_file(self, data: Dict[str, Any], output_file: str):
        """Create Excel file with structured data"""
        logger.info("Creating Excel file...")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Document Summary
            self._create_summary_sheet(writer, data)
            
            # Sheet 2: Financial Data
            self._create_financial_sheet(writer, data)
            
            # Sheet 3: Program Details
            self._create_program_sheet(writer, data)
            
            # Sheet 4: Raw Text
            self._create_raw_text_sheet(writer, data)
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, data: Dict[str, Any]):
        """Create document summary sheet"""
        summary_data = []
        
        # Add metadata
        for key, value in data['metadata'].items():
            summary_data.append({
                'Field': key.replace('_', ' ').title(),
                'Value': value
            })
        
        # Add program details
        for key, value in data['program_details'].items():
            summary_data.append({
                'Field': key.replace('_', ' ').title(),
                'Value': value
            })
        
        # Add extraction info
        summary_data.extend([
            {'Field': 'Extraction Date', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Field': 'Total Financial Items', 'Value': len(data['financial_data'])},
            {'Field': 'Document Type', 'Value': 'Reprogramming Action'},
        ])
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Document Summary', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Document Summary']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 50
    
    def _create_financial_sheet(self, writer: pd.ExcelWriter, data: Dict[str, Any]):
        """Create financial data sheet"""
        if not data['financial_data']:
            # Create empty sheet with headers
            empty_data = pd.DataFrame(columns=['Item', 'Amount', 'Amount (Text)', 'Context'])
            empty_data.to_excel(writer, sheet_name='Financial Data', index=False)
        else:
            df = pd.DataFrame(data['financial_data'])
            df.columns = ['Item', 'Amount', 'Amount (Text)', 'Context']
            df.to_excel(writer, sheet_name='Financial Data', index=False)
            
            # Format the sheet
            worksheet = writer.sheets['Financial Data']
            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 15
            worksheet.column_dimensions['C'].width = 20
            worksheet.column_dimensions['D'].width = 40
    
    def _create_program_sheet(self, writer: pd.ExcelWriter, data: Dict[str, Any]):
        """Create program details sheet"""
        program_data = []
        
        # Add narrative
        program_data.append({
            'Category': 'Narrative',
            'Description': data['narrative']
        })
        
        # Add program details
        for key, value in data['program_details'].items():
            program_data.append({
                'Category': key.replace('_', ' ').title(),
                'Description': str(value)
            })
        
        df = pd.DataFrame(program_data)
        df.to_excel(writer, sheet_name='Program Details', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Program Details']
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 60
    
    def _create_raw_text_sheet(self, writer: pd.ExcelWriter, data: Dict[str, Any]):
        """Create raw text sheet"""
        # Split text into chunks for better readability
        text_chunks = []
        raw_text = data['raw_text']
        chunk_size = 1000
        
        for i in range(0, len(raw_text), chunk_size):
            chunk = raw_text[i:i+chunk_size]
            text_chunks.append({
                'Chunk': i // chunk_size + 1,
                'Text': chunk
            })
        
        df = pd.DataFrame(text_chunks)
        df.to_excel(writer, sheet_name='Raw Text', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Raw Text']
        worksheet.column_dimensions['A'].width = 10
        worksheet.column_dimensions['B'].width = 100


def main():
    """Example usage of the transformer"""
    # Sample OCR text (replace with actual OCR output)
    sample_ocr_text = """
    === PAGE 1 ===
    Unclassified REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

    Subject: Israel Security Replacement Transfer Fund Tranche 3 DoD Serial Number:

    Appropriation Title: Various Appropriations FY 25-08 IR

    Includes Transfer?
    Yes

    Component Serial Number: (Amounts in Thousands of Dollars)
    Program Base Reflecting Program Previously Reprogramming Action Revised Program
    Congressional Action Approved by Sec Def

    This reprogramming action provides funding for the replacement of defense articles from the stocks of the
    Department of Defense expended in support of Israel and for the reimbursement of defense services of the
    Department of Defense provided to Israel or identified and notified to Congress for provision to Israel. This
    action is determined to be necessary in the national interest. This reprogramming action meets all
    administrative and legal requirements, and none of the items have been previously denied by the Congress.

    This reprogramming action transfers $657.
    """
    
    # Create transformer
    transformer = PDFToExcelTransformer()
    
    # Transform to Excel
    output_file = transformer.transform_ocr_to_excel(sample_ocr_text)
    print(f"Excel file created: {output_file}")


if __name__ == "__main__":
    main()