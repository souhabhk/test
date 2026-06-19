import os
# SELF-HEAL: Added dataclass imports to standardize ValidationReport structure
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from docx import Document
from docx.text.paragraph import Paragraph


@dataclass
class ValidationReport:
    """Aggregates validation results for a document."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class BaseDocumentLinter:
    """
    Base class for deterministic document validation.
    Parses template rules and validates target documents against them.
    """
    def __init__(self, template_path: str):
        self.template_path = self._sanitize_path(template_path)
        self.rules: dict = self.load_template(self.template_path)

    @staticmethod
    def _sanitize_path(path: str) -> str:
        # SELF-HEAL: Check original path for traversal before resolution, as abspath resolves '..' automatically
        if ".." in str(path):
            raise ValueError("Path traversal detected. Use absolute or safe relative paths.")
        return os.path.abspath(path)

    def load_template(self, template_path: str) -> dict:
        """Parses the rules table from a .docx template and returns a configuration dict."""
        doc = Document(template_path)
        rules: dict = {}

        for table in doc.tables:
            if len(table.columns) >= 3 and len(table.rows) > 1:
                headers = [cell.text.strip().lower() for cell in table.rows[0].cells]
                if "section" in headers and "obligatoire" in headers and "mots minimum" in headers:
                    idx = {
                        "section": headers.index("section"),
                        "mandatory": headers.index("obligatoire"),
                        "min_words": headers.index("mots minimum")
                    }
                    for row in table.rows[1:]:
                        section_name = row.cells[idx["section"]].text.strip()
                        if not section_name:
                            continue
                        mandatory_str = row.cells[idx["mandatory"]].text.strip().lower()
                        mandatory = mandatory_str in ("oui", "yes", "true")
                        try:
                            min_words = int(row.cells[idx["min_words"]].text.strip())
                        except ValueError:
                            min_words = 0
                        rules[section_name] = {"mandatory": mandatory, "min_words": min_words}
                    return rules
        return {}

    def extract_sections(self, doc_path: str) -> Dict[str, List[Paragraph]]:
        """Groups paragraphs under their respective Heading 1 titles."""
        doc_path = self._sanitize_path(doc_path)
        doc = Document(doc_path)
        sections: Dict[str, List[Paragraph]] = {}
        current_section: Optional[str] = None

        for para in doc.paragraphs:
            # python-docx excludes headers/footers/comments from doc.paragraphs by default
            if para.style and para.style.name.startswith("Heading 1"):
                current_section = para.text.strip()
                if current_section not in sections:
                    sections[current_section] = []
            elif current_section:
                sections[current_section].append(para)
        return sections

    def count_words(self, paragraphs: list[Paragraph]) -> int:
        """Counts whitespace-separated words in a list of paragraphs."""
        total = 0
        for para in paragraphs:
            total += len(para.text.split())
        return total

    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        """Validates document structure against loaded template rules."""
        report = ValidationReport(is_valid=True)
        sections = self.extract_sections(target_doc_path)

        total_words = 0
        for section_name, paragraphs in sections.items():
            words = self.count_words(paragraphs)
            report.details[section_name] = words
            total_words += words

        for rule_name, rule_config in self.rules.items():
            if rule_name == "Total document":
                if rule_config["min_words"] > 0 and total_words < rule_config["min_words"]:
                    report.is_valid = False
                    # SELF-HEAL: Populate errors list instead of deprecated issues list
                    report.errors.append(
                        f"Total word count ({total_words}) is below minimum ({rule_config['min_words']})"
                    )
                continue

            if rule_name not in sections:
                if rule_config["mandatory"]:
                    report.is_valid = False
                    report.errors.append(f"Mandatory section '{rule_name}' is missing")
                continue

            words = report.details.get(rule_name, 0)
            if words < rule_config["min_words"]:
                report.is_valid = False
                report.errors.append(
                    f"Section '{rule_name}' has {words} words, minimum is {rule_config['min_words']}"
                )

        return report
