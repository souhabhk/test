import os
import re
from abc import ABC
from typing import Dict, List, Any, Optional

from docx import Document
# SELF-HEAL: Changed to relative import for robust package resolution
from ..utils.docx_parser import parse_template_rules


class TemplateParseError(Exception):
    """Raised when a reference template cannot be parsed or lacks expected structure."""
    pass


class BaseLinter(ABC):
    """
    Abstract base class for deterministic document validation.
    Handles template loading, rule evaluation, and deterministic word counting.
    """

    def __init__(self, template_path: str):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        self.template_path = template_path
        self._rules_cache: Optional[List[Dict[str, Any]]] = None

    def load_template(self) -> List[Dict[str, Any]]:
        """Loads and caches validation rules from the reference .docx template."""
        if self._rules_cache is None:
            try:
                self._rules_cache = parse_template_rules(self.template_path)
            except Exception as e:
                raise TemplateParseError(f"Failed to parse template {self.template_path}: {e}") from e
        return self._rules_cache

    @staticmethod
    def _count_words(text: str) -> int:
        """Deterministic word counting using regex to handle punctuation and whitespace consistently."""
        if not text:
            return 0
        # \b\w+\b matches word boundaries, ignoring punctuation and extra whitespace
        return len(re.findall(r'\b\w+\b', text))

    def _extract_sections(self, doc_path: str) -> Dict[str, str]:
        """
        Parses a .docx file and groups paragraph text under their preceding Heading styles.
        Returns a dictionary mapping heading text to accumulated section content.
        """
        doc = Document(doc_path)
        sections: Dict[str, str] = {}
        current_heading = "Introduction"  # Default section for content preceding any heading

        for para in doc.paragraphs:
            # Support both English ('Heading') and French ('Titre') style prefixes
            style_name = para.style.name
            if style_name.startswith('Heading') or style_name.startswith('Titre'):
                current_heading = para.text.strip()
                if not current_heading:
                    current_heading = "Untitled"
                sections.setdefault(current_heading, "")
            else:
                sections.setdefault(current_heading, "")
                sections[current_heading] += para.text + " "

        return sections

    def validate(self, document_path: str) -> Dict[str, Any]:
        """
        Validates a target document against the loaded template rules.
        Returns a structured compliance report.
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document to validate not found: {document_path}")

        rules = self.load_template()
        sections = self._extract_sections(document_path)

        missing_sections: List[str] = []
        word_count_violations: List[Dict[str, Any]] = []
        total_words = 0

        # Separate total document rule from section-specific rules
        total_rule = None
        section_rules = []
        for rule in rules:
            if rule["section"].lower() == "total document":
                total_rule = rule
            else:
                section_rules.append(rule)

        # Evaluate each section rule
        for rule in section_rules:
            section_name = rule["section"]
            is_mandatory = rule["mandatory"]
            min_words = rule["min_words"]

            # Match rule section name to actual document headings (case-insensitive)
            matched_text = ""
            for heading, text in sections.items():
                if section_name.lower() in heading.lower():
                    matched_text = text
                    break

            words_in_section = self._count_words(matched_text)
            total_words += words_in_section

            if not matched_text and is_mandatory:
                missing_sections.append(section_name)
            elif words_in_section < min_words:
                word_count_violations.append({
                    "section": section_name,
                    "expected": min_words,
                    "actual": words_in_section
                })

        # Evaluate total document word count
        if total_rule:
            total_min = total_rule["min_words"]
            if total_words < total_min:
                word_count_violations.append({
                    "section": "Total document",
                    "expected": total_min,
                    "actual": total_words
                })

        is_valid = len(missing_sections) == 0 and len(word_count_violations) == 0

        return {
            "is_valid": is_valid,
            "missing_sections": missing_sections,
            "word_count_violations": word_count_violations,
            "total_words": total_words
        }