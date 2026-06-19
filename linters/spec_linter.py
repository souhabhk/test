import re
# SELF-HEAL: Removed duplicate ValidationReport definition; import from base_linter instead

from .base_linter import BaseDocumentLinter, ValidationReport

class SpecLinter(BaseDocumentLinter):
    """
    Deterministic linter for SPEC documents.
    Validates structural compliance, mandatory sections, word counts,
    and SPEC-specific rules (e.g., functional requirement identifiers).
    """
    
    # Pattern for functional requirement identifiers (e.g., EF-1, EF-42)
    EF_PATTERN = re.compile(r'\bEF-\d+\b', re.IGNORECASE)
    FUNCTIONAL_REQ_SECTION = "Exigences fonctionnelles"

    def __init__(self, template_path: str):
        """
        Initialize the SpecLinter with a path to the reference SPEC template.
        """
        super().__init__(template_path)

    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        """
        Validates the target SPEC document against the loaded template rules
        and applies SPEC-specific constraints.
        """
        # 1. Run base validation (mandatory sections, word counts, heading structure)
        base_report = super().validate_structure(target_doc_path)
        
        errors = list(base_report.errors)
        warnings = list(base_report.warnings)
        details = dict(base_report.details)
        
        # 2. Extract sections for SPEC-specific checks
        sections = self.extract_sections(target_doc_path)
        functional_req_paragraphs = sections.get(self.FUNCTIONAL_REQ_SECTION, [])
        
        if functional_req_paragraphs:
            # Combine text from all paragraphs in the section to handle split IDs
            functional_text = " ".join([p.text for p in functional_req_paragraphs])
            matches = self.EF_PATTERN.findall(functional_text)
            
            if not matches:
                errors.append(
                    f"Section '{self.FUNCTIONAL_REQ_SECTION}' must contain at least one "
                    "functional requirement identifier matching the pattern 'EF-<n>' (e.g., EF-1)."
                )
            else:
                details[f"{self.FUNCTIONAL_REQ_SECTION}_identifiers"] = matches
        else:
            # If the section is completely missing, base validation should flag it as mandatory.
            # We add a specific warning for clarity.
            warnings.append(f"Section '{self.FUNCTIONAL_REQ_SECTION}' is missing or empty.")

        # 3. Compile final report
        is_valid = len(errors) == 0 and base_report.is_valid
        return ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            details=details
        )
