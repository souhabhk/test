import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from docx import Document


@dataclass
class ValidationIssue:
    section: str
    rule: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    section_stats: Dict[str, Dict] = field(default_factory=dict)

    def add_issue(self, section: str, rule: str, message: str, expected: Optional[str] = None, actual: Optional[str] = None) -> None:
        self.is_valid = False
        self.issues.append(ValidationIssue(section, rule, message, expected, actual))


class BaseDocumentLinter:
    """Shared logic for template parsing, heading extraction, word counting, and rule evaluation."""

    def __init__(self, template_path: str) -> None:
        if not template_path.endswith('.docx'):
            raise ValueError("Template must be a .docx file")
        self.template_path = os.path.abspath(template_path)
        self.rules: Dict[str, Dict] = {}
        self.load_template(self.template_path)

    def load_template(self, template_path: str) -> Dict[str, Dict]:
        """Parses the rules table from the template document."""
        doc = Document(template_path)
        rules_config: Dict[str, Dict] = {}
        rules_found = False

        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                # Skip header row
                if cells[0].lower() == 'section':
                    continue
                if not cells[0] or len(cells) < 3:
                    continue

                section_name = cells[0]
                mandatory_str = cells[1].lower()
                min_words_str = cells[2].strip()

                mandatory = mandatory_str in ('oui', 'true', 'yes', '1')
                try:
                    min_words = int(min_words_str)
                except ValueError:
                    min_words = 0

                rules_config[section_name] = {
                    "mandatory": mandatory,
                    "min_words": min_words
                }
                rules_found = True

        if not rules_found:
            raise ValueError(f"No validation rules table found in template: {template_path}")

        self.rules = rules_config
        return self.rules

    def extract_sections(self, doc_path: str) -> Dict[str, List]:
        """Iterates through paragraphs, groups content by Heading 1."""
        if not doc_path.endswith('.docx'):
            raise ValueError("Target document must be a .docx file")

        doc = Document(doc_path)
        sections: Dict[str, List] = {}
        current_section: Optional[str] = None

        for paragraph in doc.paragraphs:
            # Check specifically for Heading 1 style (case-insensitive for robustness)
            if paragraph.style.name.lower() == 'heading 1':
                current_section = paragraph.text.strip()
                if current_section and current_section not in sections:
                    sections[current_section] = []
            elif current_section:
                sections[current_section].append(paragraph)

        return sections

    def count_words(self, paragraphs: List) -> int:
        """Counts words in a list of paragraphs deterministically."""
        total = 0
        for p in paragraphs:
            total += len(p.text.split())
        return total

    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        """Compares extracted sections against template rules, checks mandatory presence & word thresholds."""
        report = ValidationReport()
        sections = self.extract_sections(target_doc_path)

        # Initialize stats for all expected sections
        for sec_name in self.rules:
            report.section_stats[sec_name] = {
                "found": False,
                "word_count": 0,
                "mandatory": self.rules[sec_name]["mandatory"]
            }

        # Evaluate found sections against rules
        for section_name, paragraphs in sections.items():
            if section_name in self.rules:
                word_count = self.count_words(paragraphs)
                report.section_stats[section_name].update({
                    "found": True,
                    "word_count": word_count
                })

                rule = self.rules[section_name]
                if word_count < rule["min_words"]:
                    report.add_issue(
                        section=section_name,
                        rule="min_words",
                        message=f"Section '{section_name}' has {word_count} words, minimum required is {rule['min_words']}.",
                        expected=str(rule["min_words"]),
                        actual=str(word_count)
                    )

        # Check for missing mandatory sections
        for section_name, rule in self.rules.items():
            if section_name not in sections:
                if rule["mandatory"]:
                    report.add_issue(
                        section=section_name,
                        rule="mandatory_presence",
                        message=f"Mandatory section '{section_name}' is missing.",
                        expected="Present",
                        actual="Missing"
                    )

        return report