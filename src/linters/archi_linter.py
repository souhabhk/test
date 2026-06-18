import os
from typing import Union, Dict, Any

# SELF-HEAL: Changed to relative import for consistency and package safety
from .base_linter import BaseLinter


class ArchiLinter(BaseLinter):
    """
    Concrete linter for Architecture documents.
    Extends BaseLinter to enforce structural and content rules defined in template_archi.docx.
    """

    def __init__(self) -> None:
        # Resolve template path relative to the project structure (src/templates/)
        _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _template_path = os.path.join(_base_dir, "templates", "template_archi.docx")
        super().__init__(_template_path)

    def validate(self, document_path_or_bytes: Union[str, bytes]) -> Dict[str, Any]:
        """
        Validates an architecture document against the loaded template rules.
        
        Args:
            document_path_or_bytes: Path to the .docx file or raw bytes.
            
        Returns:
            A structured validation report containing:
            - valid (bool): Overall compliance status.
            - missing_sections (list): Sections marked mandatory but absent.
            - word_count_violations (list): Sections failing minimum word count.
            - total_words (int): Total word count of the document.
        """
        # SELF-HEAL: BaseLinter.validate expects a string path. Handle bytes input safely via temp file.
        if isinstance(document_path_or_bytes, bytes):
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(document_path_or_bytes)
                doc_path = tmp.name
        else:
            doc_path = document_path_or_bytes
            
        try:
            # SELF-HEAL: Wrapped validation in try/finally to ensure temp file cleanup on success or failure
            report = super().validate(doc_path)
        finally:
            if isinstance(document_path_or_bytes, bytes):
                os.unlink(doc_path)
                
        return report