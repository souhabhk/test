"""Architecture document linter implementation."""

import re
from typing import List, Dict, Any
# SELF-HEAL: Use relative imports for package consistency
from .base_linter import BaseDocumentLinter, ValidationReport


class ArchiLinter(BaseDocumentLinter):
    """Deterministic linter for Architecture documents."""

    COMPONENT_SECTION_NAME = "Composants"
    # Primary keywords expected in component descriptions
    PRIMARY_KEYWORDS = ["responsabilité", "technologie"]
    # Fallback terms for deterministic scoring when phrasing varies
    FALLBACK_KEYWORDS = [
        "responsable", "charge", "rôle", "fonction",
        "tech", "stack", "framework", "langage", "outil", "librairie"
    ]

    def __init__(self, template_path: str = "templates/archi_template.docx"):
        # SELF-HEAL: Pass template_path to base class which now accepts it
        super().__init__(template_path)

    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        """
        Validates the architecture document against template rules and
        enforces specific component detailing requirements.
        """
        # Run base structural & word-count validation
        report = super().validate_structure(target_doc_path)
        sections = self.extract_sections(target_doc_path)

        if self.COMPONENT_SECTION_NAME not in sections:
            report.warnings.append(
                f"Section '{self.COMPONENT_SECTION_NAME}' missing. Component validation skipped."
            )
            return report

        paragraphs = sections[self.COMPONENT_SECTION_NAME]
        section_text = " ".join([p.text for p in paragraphs])

        # Identify missing primary keywords (case-insensitive)
        missing_primary = [
            kw for kw in self.PRIMARY_KEYWORDS
            if not re.search(re.escape(kw), section_text, re.IGNORECASE)
        ]

        if missing_primary:
            # Fallback scoring: count matches of alternative phrasing
            fallback_matches = sum(
                1 for kw in self.FALLBACK_KEYWORDS
                if re.search(re.escape(kw), section_text, re.IGNORECASE)
            )

            # If fallback coverage meets or exceeds missing keywords, warn instead of error
            if fallback_matches >= len(missing_primary):
                report.warnings.append(
                    f"Section '{self.COMPONENT_SECTION_NAME}' uses alternative phrasing for: "
                    f"{', '.join(missing_primary)}. Consider using standard terms for consistency."
                )
            else:
                report.errors.append(
                    f"Section '{self.COMPONENT_SECTION_NAME}' lacks required details. "
                    f"Missing keywords: {', '.join(missing_primary)}."
                )

        return report