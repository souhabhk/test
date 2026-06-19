from .spec_linter import SpecLinter
from .archi_linter import ArchiLinter
# SELF-HEAL: Import ValidationReport for accurate type hinting
from .base_linter import ValidationReport

__all__ = ["SpecLinter", "ArchiLinter", "validate_document"]


def validate_document(doc_path: str, doc_type: str) -> ValidationReport:
    """
    Validates a generated document against its corresponding reference template.
    
    Args:
        doc_path: Absolute or relative path to the .docx file to validate.
        doc_type: Document category ('spec' or 'archi').
        
    Returns:
        Validation report containing success status and detailed issues.
    """
    doc_type = doc_type.strip().lower()
    # SELF-HEAL: Pass required template_path argument to linter constructors
    if doc_type == "spec":
        linter = SpecLinter("templates/spec_template.docx")
    elif doc_type == "archi":
        linter = ArchiLinter("templates/archi_template.docx")
    else:
        raise ValueError(f"Unsupported document type '{doc_type}'. Expected 'spec' or 'archi'.")
        
    return linter.validate_structure(doc_path)