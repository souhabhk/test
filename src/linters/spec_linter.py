import re
from pathlib import Path
from typing import Union, Dict, Any, List

from docx import Document
from .base_linter import BaseLinter

class SpecLinter(BaseLinter):
    """
    Concrete linter for SPEC documents.
    Extends BaseLinter to enforce SPEC-specific structural and content rules.
    """
    TEMPLATE_FILENAME = "template_spec.docx"
    FUNCTIONAL_REQ_HEADING = "Exigences fonctionnelles"
    REQUIREMENT_ID_PATTERN = re.compile(r"EF-\d+")

    def __init__(self, template_dir: Union[str, Path] = None):
        if template_dir is None:
            template_dir = Path(__file__).resolve().parent.parent / "templates"
        template_path = Path(template_dir) / self.TEMPLATE_FILENAME
        # SELF-HEAL: Ensure template_path is passed as string to BaseLinter
        super().__init__(template_path=str(template_path))

    def validate(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validates the SPEC document against template rules and SPEC-specific constraints.
        Returns a structured compliance report.
        """
        report = super().validate(str(document_path))
        
        # SPEC-specific validation: Check for requirement IDs in Functional Requirements section
        req_validation = self._validate_requirement_ids(document_path)
        report["requirement_id_violations"] = req_validation["violations"]
        
        # Update overall validity if SPEC-specific rules fail
        if req_validation["violations"]:
            report["valid"] = False
            
        return report

    def _validate_requirement_ids(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Checks if the 'Exigences fonctionnelles' section contains at least one requirement ID matching EF-<n>.
        """
        violations: List[str] = []
        try:
            doc = Document(str(document_path))
            # SELF-HEAL: Use inherited _extract_section_text instead of redefining it
            section_text = self._extract_section_text(doc, self.FUNCTIONAL_REQ_HEADING)
            
            if not section_text:
                violations.append(f"Section '{self.FUNCTIONAL_REQ_HEADING}' not found or empty.")
                return {"violations": violations}
                
            if not self.REQUIREMENT_ID_PATTERN.search(section_text):
                violations.append(f"No requirement ID matching pattern 'EF-<n>' found in '{self.FUNCTIONAL_REQ_HEADING}'.")
                
        except Exception as e:
            violations.append(f"Error during requirement ID validation: {str(e)}")
            
        return {"violations": violations}