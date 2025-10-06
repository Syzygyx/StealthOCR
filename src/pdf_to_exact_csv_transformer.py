"""
PDF OCR to Exact CSV Transformer
Converts OCR extracted text from PDFs into the exact CSV format required
"""

import re
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToExactCSVTransformer:
    """
    Transforms OCR extracted text from PDFs into the exact CSV format
    """
    
    def __init__(self):
        self.csv_columns = [
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
        ]
    
    def transform_ocr_to_csv(self, ocr_text: str, output_file: str = None, source_file: str = None) -> str:
        """
        Transform OCR text to exact CSV format
        
        Args:
            ocr_text: Raw OCR extracted text
            output_file: Output CSV file path (optional)
            source_file: Source PDF file path for the 'file' column
            
        Returns:
            Path to created CSV file
        """
        logger.info("Starting OCR to exact CSV transformation...")
        
        # Parse the OCR text
        parsed_data = self._parse_ocr_text(ocr_text)
        
        # Create CSV file
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"stealth_ocr_output_{timestamp}.csv"
        
        self._create_csv_file(parsed_data, output_file, source_file)
        
        logger.info(f"CSV file created: {output_file}")
        return output_file
    
    def _parse_ocr_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse OCR text and extract structured data for each appropriation line"""
        logger.info("Parsing OCR text for appropriation data...")
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Extract appropriation data
        appropriation_data = self._extract_appropriation_data(cleaned_text)
        
        return appropriation_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # In certain contexts
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _extract_appropriation_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract appropriation data from the text"""
        appropriation_data = []
        
        # Look for any reprogramming action (not just Israel-specific)
        if any(keyword in text.upper() for keyword in ["REPROGRAMMING ACTION", "ARMY INCREASE", "NAVY INCREASE", "AIR FORCE INCREASE", "DEFENSE-WIDE INCREASE"]):
            # Extract the main document info
            doc_info = self._extract_document_info(text)
            
            # Extract individual appropriation lines
            lines = self._extract_appropriation_lines(text)
            
            for line in lines:
                row_data = {
                    'appropriation_category': line.get('category', ''),
                    'appropriation code': line.get('code', ''),
                    'appropriation activity': line.get('activity', ''),
                    'branch': line.get('branch', ''),
                    'fiscal_year_start': line.get('fiscal_year_start', '2025'),
                    'fiscal_year_end': line.get('fiscal_year_end', '2025'),
                    'budget_activity_number': line.get('budget_activity_number', ''),
                    'budget_activity_title': line.get('budget_activity_title', ''),
                    'pem': line.get('pem', ''),
                    'budget_title': line.get('budget_title', ''),
                    'program_base_congressional': line.get('program_base_congressional', ''),
                    'program_base_dod': line.get('program_base_dod', ''),
                    'reprogramming_amount': line.get('reprogramming_amount', ''),
                    'revised_program_total': line.get('revised_program_total', ''),
                    'explanation': line.get('explanation', ''),
                    'file': doc_info.get('file', '')
                }
                appropriation_data.append(row_data)
        
        return appropriation_data
    
    def _extract_document_info(self, text: str) -> Dict[str, str]:
        """Extract document-level information"""
        info = {}
        
        # Extract document title
        title_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if title_match:
            info['title'] = title_match.group(1).strip()
        
        # Extract serial number
        serial_match = re.search(r'DoD Serial Number:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if serial_match:
            info['serial'] = serial_match.group(1).strip()
        
        # Extract appropriation title
        appropriation_match = re.search(r'Appropriation Title:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if appropriation_match:
            info['appropriation_title'] = appropriation_match.group(1).strip()
        
        # Set file path (will be updated by caller)
        info['file'] = 'https://example.com/document.pdf'
        
        return info
    
    def _extract_appropriation_lines(self, text: str) -> List[Dict[str, str]]:
        """Extract individual appropriation lines from the text"""
        lines = []
        
        # Look for ARMY INCREASE section
        army_section = self._extract_section(text, r'ARMY INCREASE', r'NAVY INCREASE|AIR FORCE INCREASE|DEFENSE-WIDE INCREASE|$')
        if army_section:
            army_line = self._parse_appropriation_line(army_section, 'Army', 'Operation and Maintenance')
            if army_line:
                lines.append(army_line)
        
        # Look for NAVY INCREASE section
        navy_section = self._extract_section(text, r'NAVY INCREASE', r'AIR FORCE INCREASE|DEFENSE-WIDE INCREASE|$')
        if navy_section:
            navy_line = self._parse_appropriation_line(navy_section, 'Navy', 'Weapons Procurement')
            if navy_line:
                lines.append(navy_line)
        
        # Look for AIR FORCE INCREASE sections
        air_force_sections = self._extract_multiple_sections(text, r'AIR FORCE INCREASE', r'DEFENSE-WIDE INCREASE|$')
        for section in air_force_sections:
            air_force_line = self._parse_appropriation_line(section, 'Air Force', 'Missile Procurement')
            if air_force_line:
                lines.append(air_force_line)
        
        # Look for DEFENSE-WIDE INCREASE section
        defense_wide_section = self._extract_section(text, r'DEFENSE-WIDE INCREASE', r'DEFENSE-WIDE DECREASE|$')
        if defense_wide_section:
            defense_wide_line = self._parse_appropriation_line(defense_wide_section, 'Defense-Wide', 'Procurement')
            if defense_wide_line:
                lines.append(defense_wide_line)
        
        # Look for DEFENSE-WIDE DECREASE section
        defense_wide_decrease_section = self._extract_section(text, r'DEFENSE-WIDE DECREASE', r'$')
        if defense_wide_decrease_section:
            decrease_line = self._parse_appropriation_line(defense_wide_decrease_section, 'Defense-Wide', 'Operation and Maintenance', is_decrease=True)
            if decrease_line:
                lines.append(decrease_line)
        
        return lines
    
    def _extract_section(self, text: str, start_pattern: str, end_pattern: str) -> str:
        """Extract a section of text between two patterns"""
        start_match = re.search(start_pattern, text, re.IGNORECASE)
        if not start_match:
            return ""
        
        start_pos = start_match.end()
        end_match = re.search(end_pattern, text[start_pos:], re.IGNORECASE)
        
        if end_match:
            return text[start_pos:start_pos + end_match.start()].strip()
        else:
            return text[start_pos:].strip()
    
    def _extract_multiple_sections(self, text: str, start_pattern: str, end_pattern: str) -> List[str]:
        """Extract multiple sections with the same start pattern"""
        sections = []
        start_matches = list(re.finditer(start_pattern, text, re.IGNORECASE))
        
        for i, start_match in enumerate(start_matches):
            start_pos = start_match.end()
            
            # Find the next start pattern or end pattern
            next_start = start_matches[i + 1].start() if i + 1 < len(start_matches) else len(text)
            end_match = re.search(end_pattern, text[start_pos:next_start], re.IGNORECASE)
            
            if end_match:
                section_text = text[start_pos:start_pos + end_match.start()].strip()
            else:
                section_text = text[start_pos:next_start].strip()
            
            if section_text:
                sections.append(section_text)
        
        return sections
    
    def _parse_appropriation_line(self, section_text: str, branch: str, category: str, is_decrease: bool = False) -> Dict[str, str]:
        """Parse an individual appropriation line from section text"""
        line_data = {
            'category': category,
            'code': '',
            'activity': '',
            'branch': branch,
            'fiscal_year_start': '2025',
            'fiscal_year_end': '2025',
            'budget_activity_number': '',
            'budget_activity_title': '',
            'pem': '',
            'budget_title': '',
            'program_base_congressional': '',
            'program_base_dod': '',
            'reprogramming_amount': '',
            'revised_program_total': '',
            'explanation': ''
        }
        
        # Extract budget activity
        budget_activity_match = re.search(r'Budget Activity (\d+):\s*(.+?)(?:\n|$)', section_text, re.IGNORECASE)
        if budget_activity_match:
            line_data['budget_activity_number'] = budget_activity_match.group(1)
            line_data['budget_activity_title'] = budget_activity_match.group(2).strip()
        
        # Extract budget title
        budget_title_match = re.search(r'Budget Activity \d+:\s*.+?\n(.+?)(?:\n|$)', section_text, re.IGNORECASE | re.DOTALL)
        if budget_title_match:
            line_data['budget_title'] = budget_title_match.group(1).strip()
        
        # Extract amounts
        amounts = self._extract_amounts(section_text)
        if amounts:
            line_data['program_base_congressional'] = amounts.get('program_base', '')
            line_data['program_base_dod'] = amounts.get('program_base', '')
            line_data['reprogramming_amount'] = amounts.get('reprogramming', '')
            line_data['revised_program_total'] = amounts.get('revised_total', '')
        
        # Extract explanation
        explanation_match = re.search(r'Explanation:\s*(.+?)(?:\n\n|$)', section_text, re.IGNORECASE | re.DOTALL)
        if explanation_match:
            line_data['explanation'] = explanation_match.group(1).strip()
        
        # Handle decrease amounts
        if is_decrease:
            decrease_amount = self._extract_decrease_amount(section_text)
            if decrease_amount:
                line_data['reprogramming_amount'] = f"-{decrease_amount}"
        
        return line_data
    
    def _extract_amounts(self, text: str) -> Dict[str, str]:
        """Extract financial amounts from text"""
        amounts = {}
        
        # Look for reprogramming amount
        reprogramming_match = re.search(r'\+([\d,]+)', text)
        if reprogramming_match:
            amounts['reprogramming'] = reprogramming_match.group(1)
        
        # Look for program base (if available)
        program_base_match = re.search(r'Program Base[:\s]*([\d,]+)', text, re.IGNORECASE)
        if program_base_match:
            amounts['program_base'] = program_base_match.group(1)
        
        # Calculate revised total if we have both
        if amounts.get('program_base') and amounts.get('reprogramming'):
            try:
                base = int(amounts['program_base'].replace(',', ''))
                reprogramming = int(amounts['reprogramming'].replace(',', ''))
                amounts['revised_total'] = f"{base + reprogramming:,}"
            except ValueError:
                pass
        
        return amounts
    
    def _extract_decrease_amount(self, text: str) -> str:
        """Extract decrease amount from text"""
        decrease_match = re.search(r'-([\d,]+)', text)
        if decrease_match:
            return decrease_match.group(1)
        return ''
    
    def _create_csv_file(self, data: List[Dict[str, Any]], output_file: str, source_file: str = None):
        """Create CSV file with exact format"""
        logger.info("Creating CSV file...")
        
        # Update file paths if source file provided
        if source_file:
            for row in data:
                row['file'] = source_file
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Ensure all columns are present
        for col in self.csv_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns to match exact format
        df = df[self.csv_columns]
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        logger.info(f"CSV file created with {len(df)} rows and {len(df.columns)} columns")


def main():
    """Example usage of the transformer"""
    # Sample OCR text (replace with actual OCR output)
    sample_ocr_text = """
    === PAGE 1 ===
    Unclassified REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

    Subject: Israel Security Replacement Transfer Fund Tranche 3
    DoD Serial Number: 2024-001

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

    This reprogramming action transfers $657,000.
    """
    
    # Create transformer
    transformer = PDFToExactCSVTransformer()
    
    # Transform to CSV
    output_file = transformer.transform_ocr_to_csv(sample_ocr_text)
    print(f"CSV file created: {output_file}")


if __name__ == "__main__":
    main()