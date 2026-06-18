import os
from typing import Any, Dict

from src.linters.base_linter import BaseLinter

# Resolve template path relative to the project structure
_LINTER_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_DIR = os.path.join(_LINTER_DIR, "..", "templates")
_ARCHI_TEMPLATE_PATH = os.path.join(_TEMPLATE_DIR, "template_archi.docx")


class ArchiLinter(BaseLinter):
    """
    Deterministic linter for Architecture documents.
    
    Extends BaseLinter to enforce structural compliance and minimum word counts
    based on the rules defined in `template_archi.docx`.
    """

    def __init__(self, template_path: str = _ARCHI_TEMPLATE_PATH) -> None:
        # SELF-HEAL: Removed unsupported 'doc_type' argument from super().__init__ call
        super().__init__(template_path=template_path)

    def validate(self, document_path: str) -> Dict[str, Any]:
        """
        Validates an architecture document against the reference template.
        
        Args:
            document_path: Absolute or relative path to the .docx file to validate.
            
        Returns:
            A structured report containing:
                - valid (bool): Overall compliance status.
                - missing_sections (List[str]): Sections marked mandatory but absent.
                - word_count_violations (List[Dict]): Sections failing minimum word count.
                - total_words (int): Actual total word count of the document.
                - errors (List[str]): Any parsing or structural errors encountered.
        """
        return super().validate(document_path)