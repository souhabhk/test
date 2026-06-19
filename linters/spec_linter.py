import re
import logging
from typing import List, Dict, Any

from .base_linter import BaseDocumentLinter, ValidationReport

logger = logging.getLogger(__name__)


class SpecLinter(BaseDocumentLinter):
    """
    SPEC-specific document linter.
    Validates structural compliance based on spec_template.docx rules
    and enforces domain-specific patterns (e.g., EF-<n> identifiers).
    """

    FUNCTIONAL_REQS_SECTION = "Exigences fonctionnelles"
    EF_PATTERN = re.compile(r'\bEF-\d+\b', re.IGNORECASE)

    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        """
        Validates the target SPEC document against template rules and SPEC-specific constraints.
        """
        # SELF-HEAL: Base class returns ValidationReport with 'issues' list, not errors/warnings/info dicts.
        # Replaced incorrect attribute access with direct report inheritance and add_issue calls.
        report = super().validate_structure(target_doc_path)

        # SPEC-specific validation: EF-<n> pattern check
        sections = self.extract_sections(target_doc_path)
        
        if self.FUNCTIONAL_REQS_SECTION in sections:
            paragraphs = sections[self.FUNCTIONAL_REQS_SECTION]
            section_text = " ".join(p.text for p in paragraphs if p.text)
            matches = self.EF_PATTERN.findall(section_text)

            if not matches:
                report.add_issue(
                    section=self.FUNCTIONAL_REQS_SECTION,
                    rule="ef_pattern",
                    message="Missing functional requirement identifiers. At least one 'EF-<n>' pattern is required."
                )
            else:
                logger.info(f"Found {len(matches)} functional requirement identifier(s): {', '.join(matches)}")
        else:
            # Base validation already flags missing mandatory sections.
            pass

        return report