"""
Utility module for parsing .docx templates used in deterministic linting.
Extracts heading hierarchies and validation rules tables from reference documents.
"""

from typing import List, Dict, Any, Optional
from docx import Document


class TemplateParseError(Exception):
    """Raised when a .docx template does not conform to the expected structure."""
    pass


class DocxParser:
    """
    Parses a .docx template to extract expected headings and validation rules.
    Results are cached in memory after the first instantiation to avoid repeated I/O.
    """

    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self._headings: Optional[List[str]] = None
        self._rules: Optional[List[Dict[str, Any]]] = None
        self._parse()

    def _parse(self) -> None:
        """Loads the document and triggers extraction of headings and rules."""
        try:
            self._doc = Document(self.docx_path)
        # SELF-HEAL: Replaced non-existent PackageNotFoundError import with generic Exception catch for python-docx compatibility
        except Exception as e:
            raise TemplateParseError(f"Failed to open document: {e}") from e

        self._extract_headings()
        self._parse_rules_table()

    def _extract_headings(self) -> None:
        """Extracts an ordered list of heading texts from the document."""
        headings = []
        for paragraph in self._doc.paragraphs:
            # Standard Word heading styles start with 'Heading'
            if paragraph.style.name.startswith('Heading'):
                text = paragraph.text.strip()
                if text:
                    headings.append(text)
        self._headings = headings

    def _parse_rules_table(self) -> None:
        """
        Locates the 3-column validation rules table and parses it into a list of dicts.
        Expected headers: Section | Obligatoire | Mots minimum
        """
        rules_table = None
        for table in self._doc.tables:
            if len(table.rows) < 2:
                continue
            header_cells = [cell.text.strip().lower() for cell in table.rows[0].cells]
            if 'section' in header_cells and 'obligatoire' in header_cells and 'mots minimum' in header_cells:
                rules_table = table
                break

        if rules_table is None:
            raise TemplateParseError(
                "Validation rules table not found. Expected headers: 'Section', 'Obligatoire', 'Mots minimum'."
            )

        header_lower = [cell.text.strip().lower() for cell in rules_table.rows[0].cells]
        sec_idx = header_lower.index('section')
        obl_idx = header_lower.index('obligatoire')
        min_idx = header_lower.index('mots minimum')

        rules = []
        for row in rules_table.rows[1:]:
            cells = row.cells
            if len(cells) <= max(sec_idx, obl_idx, min_idx):
                continue

            section = cells[sec_idx].text.strip()
            if not section:
                continue

            mandatory_raw = cells[obl_idx].text.strip().lower()
            mandatory = mandatory_raw in ('oui', 'yes', 'true', '1')

            min_words_raw = cells[min_idx].text.strip()
            try:
                min_words = int(min_words_raw)
            except ValueError:
                raise TemplateParseError(
                    f"Invalid word count value '{min_words_raw}' for section '{section}'."
                )

            rules.append({
                'section': section,
                'mandatory': mandatory,
                'min_words': min_words
            })
        self._rules = rules

    @property
    def headings(self) -> List[str]:
        """Returns the cached list of headings extracted from the template."""
        if self._headings is None:
            raise TemplateParseError("Headings not parsed.")
        return self._headings

    @property
    def rules(self) -> List[Dict[str, Any]]:
        """Returns the cached list of validation rules parsed from the template."""
        if self._rules is None:
            raise TemplateParseError("Rules not parsed.")
        return self._rules