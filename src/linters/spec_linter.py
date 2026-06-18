import os
import re
from pathlib import Path
from typing import Dict, Any, List

from .base_linter import BaseLinter


class SpecLinter(BaseLinter):
    """
    Concrete linter for SPEC documents.
    Extends BaseLinter to enforce SPEC-specific rules, including requirement ID validation.
    """
    
    TEMPLATE_FILENAME = "template_spec.docx"
    REQUIREMENT_ID_PATTERN = re.compile(r'\bEF-\d+\b')
    REQUIREMENTS_SECTION_NAME = "Exigences fonctionnelles"

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # SELF-HEAL: Fixed path resolution to correctly point to src/templates/ (parent.parent instead of parent)
            template_dir = str(Path(__file__).resolve().parent.parent / "templates")
        super().__init__(os.path.join(template_dir, self.TEMPLATE_FILENAME))

    def validate(self, document_path: str) -> Dict[str, Any]:
        """
        Validates the SPEC document against template rules and SPEC-specific constraints.
        
        Args:
            document_path: Path to the .docx file to validate.
            
        Returns:
            A dictionary containing validation results and actionable feedback.
        """
        # Run base validation (headings, mandatory sections, word counts)
        report = super().validate(document_path)
        
        # Run SPEC-specific validation
        spec_issues = self._validate_requirement_ids(document_path)
        
        if spec_issues:
            report.setdefault("spec_violations", []).extend(spec_issues)
            report["is_valid"] = False
            
        return report

    def _validate_requirement_ids(self, document_path: str) -> List[str]:
        """
        Ensures the 'Exigences fonctionnelles' section contains at least one requirement ID (EF-<n>).
        """
        from docx import Document
        try:
            doc = Document(document_path)
        except Exception as e:
            return [f"Erreur lors de la lecture du document : {e}"]

        in_requirements_section = False
        found_requirement_id = False

        for paragraph in doc.paragraphs:
            style_name = paragraph.style.name if paragraph.style else ""
            text = paragraph.text.strip()

            # SELF-HEAL: Added support for French 'Titre 1' heading style alongside English 'Heading 1'
            if style_name in ('Heading 1', 'Titre 1'):
                if self.REQUIREMENTS_SECTION_NAME.lower() in text.lower():
                    in_requirements_section = True
                else:
                    if in_requirements_section:
                        in_requirements_section = False
                        break  # Section ended, stop scanning

            # Check for EF-<n> pattern within the target section
            if in_requirements_section and self.REQUIREMENT_ID_PATTERN.search(text):
                found_requirement_id = True
                break

        if not found_requirement_id:
            return [
                f"La section '{self.REQUIREMENTS_SECTION_NAME}' doit contenir au moins un identifiant d'exigence (format: EF-<n>)."
            ]
        return []