import re
from dataclasses import dataclass, field
from typing import List

# SELF-HEAL: Use relative imports for package consistency
from .base_linter import BaseDocumentLinter, ValidationReport


@dataclass
class SpecValidationReport(ValidationReport):
    """Extended validation report for SPEC documents."""
    ef_identifiers_found: List[str] = field(default_factory=list)


class SpecLinter(BaseDocumentLinter):
    """
    Linter for validating SPEC documents against reference templates.
    Adds domain-specific checks such as functional requirement identifiers (EF-<n>).
    """

    def __init__(self, template_path: str = "templates/spec_template.docx"):
        # SELF-HEAL: Pass template_path to base class which now accepts it
        super().__init__(template_path)
        # Case-insensitive regex with word boundaries to avoid false positives (e.g., REF-123)
        self.ef_pattern = re.compile(r'\bEF-\d+\b', re.IGNORECASE)

    def validate_structure(self, target_doc_path: str) -> SpecValidationReport:
        """
        Validates the structure of a SPEC document.
        Checks mandatory sections, word counts, and presence of EF-<n> identifiers.
        """
        # Run base validation (mandatory sections & word counts)
        base_report = super().validate_structure(target_doc_path)
        
        # SELF-HEAL: Properly initialize subclass report with all base fields to prevent missing data
        report = SpecValidationReport(
            is_valid=base_report.is_valid,
            section_results=list(base_report.section_results),
            total_words=base_report.total_words,
            global_errors=list(base_report.global_errors),
            errors=list(base_report.errors),
            warnings=list(base_report.warnings),
            ef_identifiers_found=[]
        )
        
        # Extract sections for SPEC-specific checks
        sections = self.extract_sections(target_doc_path)
        ef_paragraphs = sections.get("Exigences fonctionnelles", [])
        
        # Combine text from all paragraphs to avoid split-boundary issues
        ef_section_content = " ".join([p.text for p in ef_paragraphs])
        
        # Find all EF-<n> identifiers
        ef_matches = self.ef_pattern.findall(ef_section_content)
        report.ef_identifiers_found = ef_matches
        
        # Validate presence of at least one identifier
        if not ef_matches:
            report.errors.append(
                "Exigences fonctionnelles: Au moins un identifiant de type 'EF-<n>' est requis."
            )
            report.is_valid = False
            
        return report