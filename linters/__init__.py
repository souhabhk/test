"""Linter package for deterministic validation of SPEC and Architecture documents."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from .base_linter import ValidationReport
from .spec_linter import SpecLinter
from .archi_linter import ArchiLinter

# SELF-HEAL: Moved alias before function definition to prevent NameError if called during import
ValidationResult = ValidationReport


def validate_document(doc_path: str, doc_type: str) -> Union[bool, ValidationResult]:
    """
    Validates a document against its corresponding template rules.
    
    Args:
        doc_path: Path to the document to validate.
        doc_type: Type of document ('spec' or 'archi').
        
    Returns:
        True if validation passes, otherwise a ValidationResult with details.
    """
    target_path = Path(doc_path).resolve()
    
    if not target_path.exists():
        return ValidationResult(is_valid=False, errors=[f"Document not found: {target_path}"])
    if target_path.suffix.lower() != ".docx":
        return ValidationResult(is_valid=False, errors=["Only .docx files are supported."])

    base_dir = Path(__file__).parent.parent
    doc_type_lower = doc_type.lower()
    
    if doc_type_lower == "spec":
        template_path = base_dir / "templates" / "spec_template.docx"
        linter = SpecLinter(template_path)
    elif doc_type_lower == "archi":
        template_path = base_dir / "templates" / "archi_template.docx"
        linter = ArchiLinter(template_path)
    else:
        return ValidationResult(is_valid=False, errors=[f"Unknown document type: {doc_type}"])

    if not template_path.exists():
        return ValidationResult(is_valid=False, errors=[f"Template not found: {template_path}"])

    result = linter.validate_structure(target_path)
    return result


__all__ = ["SpecLinter", "ArchiLinter", "ValidationResult", "validate_document"]
