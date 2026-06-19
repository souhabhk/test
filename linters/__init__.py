"""Linters package for deterministic validation of AI-generated documents."""

# SELF-HEAL: Removed unused 'os' import
from pathlib import Path

# SELF-HEAL: Use relative imports for package consistency
from .base_linter import ValidationReport
from .spec_linter import SpecLinter
from .archi_linter import ArchiLinter


def validate_document(doc_path: str, doc_type: str) -> ValidationReport:
    """
    Validates a document against the appropriate template and rules.
    
    Args:
        doc_path: Path to the .docx file to validate.
        doc_type: Type of document ('spec' or 'archi').
        
    Returns:
        ValidationReport containing results and any errors.
    """
    # Path sanitization & validation
    resolved_path = Path(doc_path).resolve()
    if not resolved_path.is_file():
        raise FileNotFoundError(f"Document not found: {resolved_path}")
    if resolved_path.suffix.lower() != ".docx":
        raise ValueError(f"Unsupported file extension: {resolved_path.suffix}. Expected .docx")

    doc_type = doc_type.lower().strip()
    if doc_type == "spec":
        linter = SpecLinter()
    elif doc_type == "archi":
        linter = ArchiLinter()
    else:
        raise ValueError(f"Unsupported document type: {doc_type}. Expected 'spec' or 'archi'.")
        
    return linter.validate_structure(str(resolved_path))


__all__ = ["SpecLinter", "ArchiLinter", "validate_document", "ValidationReport"]