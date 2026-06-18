"""
Utility module for parsing .docx templates to extract heading structures and validation rules.
"""
from pathlib import Path
from typing import List, Dict, Any, Union

from docx import Document

class TemplateParseError(Exception):
    """Raised when a .docx template fails to parse or lacks expected structure."""
    pass

class DocxParser:
    """
    Parses a .docx file to extract document headings and a structured rules table.
    Designed to read templates maintained by BA/PO.
    """
    
    def __init__(self, template_path: Union[str, Path]):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise TemplateParseError(f"Template file not found: {self.template_path}")
        try:
            self.document = Document(str(self.template_path))
        except Exception as e:
            raise TemplateParseError(f"Failed to read document: {e}") from e

    def extract_headings(self) -> List[str]:
        """
        Extracts an ordered list of heading texts from the document.
        Only paragraphs with styles starting with 'Heading' are considered.
        """
        headings = []
        for paragraph in self.document.paragraphs:
            style_name = paragraph.style.name if paragraph.style else ""
            if style_name.startswith("Heading"):
                text = paragraph.text.strip()
                if text:
                    headings.append(text)
        return headings

    def parse_rules_table(self) -> List[Dict[str, Any]]:
        """
        Parses the 3-column rules table from the document.
        Expects headers: Section | Obligatoire | Mots minimum
        Returns a list of dictionaries with keys: section, obligatoire, mots_minimum.
        """
        target_table = None
        
        for table in self.document.tables:
            if len(table.rows) < 2:
                continue
            header_texts = [cell.text.replace('\n', ' ').strip().lower() for cell in table.rows[0].cells]
            # Check for expected headers
            if "section" in header_texts and "obligatoire" in header_texts and "mots minimum" in header_texts:
                target_table = table
                break
        
        if target_table is None:
            raise TemplateParseError(
                "Rules table not found. Ensure it contains headers: Section | Obligatoire | Mots minimum"
            )
            
        rules = []
        # Iterate over data rows (skip header)
        for row in target_table.rows[1:]:
            cell_texts = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
            
            # Skip completely empty rows
            if not any(cell_texts):
                continue
                
            section = cell_texts[0] if len(cell_texts) > 0 else ""
            obligatoire_str = cell_texts[1] if len(cell_texts) > 1 else "Oui"
            mots_min_str = cell_texts[2] if len(cell_texts) > 2 else "0"
            
            if not section:
                continue
                
            # Normalize boolean
            obligatoire = obligatoire_str.lower() in ("oui", "yes", "true", "1")
            
            # Normalize integer
            try:
                mots_minimum = int(mots_min_str)
            except ValueError:
                mots_minimum = 0
                
            rules.append({
                "section": section,
                "obligatoire": obligatoire,
                "mots_minimum": mots_minimum
            })
            
        return rules