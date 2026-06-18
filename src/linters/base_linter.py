import os
import re
from abc import ABC
from typing import Dict, List, Any, Optional

from src.utils.docx_parser import DocxParser

class BaseLinter(ABC):
    """
    Abstract base class for deterministic document linters.
    Handles template loading, rule evaluation, and word counting.
    """

    def __init__(self, template_path: str):
        self._validate_docx_file(template_path)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        self.template_path = template_path
        # SELF-HEAL: Pass template_path to DocxParser constructor instead of calling it without arguments
        self._parser = DocxParser(template_path)
        self._cached_rules: Optional[List[Dict[str, Any]]] = None
        self._cached_headings: Optional[List[str]] = None

    @staticmethod
    def _validate_docx_file(path: str) -> None:
        if not path.lower().endswith('.docx'):
            raise ValueError(f"Expected .docx file, got: {path}")

    def load_template(self) -> None:
        """Loads and parses the template, caching rules and headings."""
        # SELF-HEAL: Use correct DocxParser methods instead of non-existent parse_template
        self._cached_headings = self._parser.extract_headings()
        self._cached_rules = self._parser.parse_rules_table()

    @staticmethod
    def _count_words(text: str) -> int:
        """Deterministic word count using regex to handle punctuation and whitespace."""
        if not text:
            return 0
        # SELF-HEAL: Implement deterministic word counting as specified in plan
        return len(re.findall(r'\b\w+\b', text))

    def validate(self, document_path: str) -> Dict[str, Any]:
        """
        Validates a document against the template rules.
        Returns a structured report matching the plan's requirements.
        """
        # SELF-HEAL: Implement missing validate method per plan specification
        if self._cached_rules is None or self._cached_headings is None:
            self.load_template()

        report = {
            "valid": True,
            "missing_sections": [],
            "word_count_violations": [],
            "total_words": 0,
            "errors": []
        }

        try:
            doc_parser = DocxParser(document_path)
            doc_headings = doc_parser.extract_headings()
            
            # Extract full text for total word count
            full_text = "\n".join([p.text for p in doc_parser.document.paragraphs])
            report["total_words"] = self._count_words(full_text)

            for rule in self._cached_rules:
                section_name = rule["section"]
                is_mandatory = rule["obligatoire"]
                min_words = rule["mots_minimum"]

                if section_name == "Total document":
                    if report["total_words"] < min_words:
                        report["valid"] = False
                        report["word_count_violations"].append({
                            "section": "Total document",
                            "expected": min_words,
                            "actual": report["total_words"]
                        })
                    continue

                if section_name not in doc_headings:
                    if is_mandatory:
                        report["valid"] = False
                        report["missing_sections"].append(section_name)
                    continue

                section_text = self._extract_section_text(doc_parser.document, section_name)
                actual_words = self._count_words(section_text)
                
                if actual_words < min_words:
                    report["valid"] = False
                    report["word_count_violations"].append({
                        "section": section_name,
                        "expected": min_words,
                        "actual": actual_words
                    })

        except Exception as e:
            report["valid"] = False
            report["errors"].append(str(e))

        return report

    @staticmethod
    def _extract_section_text(document, heading: str) -> str:
        """Extracts text under a specific heading until the next heading."""
        text_parts = []
        capturing = False
        for para in document.paragraphs:
            is_heading = para.style.name.startswith("Heading") if para.style else False
            # SELF-HEAL: Use exact match instead of substring to prevent false positives on similar headings
            if is_heading and para.text.strip() == heading:
                capturing = True
                continue
            if capturing:
                if is_heading:
                    break
                text_parts.append(para.text)
        return " ".join(text_parts)