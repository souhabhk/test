import re
from pathlib import Path
from typing import Any, Dict, Union

from docx import Document
# SELF-HEAL: Use absolute import for consistency with other modules and reliable module resolution
from src.linters.base_linter import BaseLinter


class SpecLinter(BaseLinter):
    """
    Linter déterministe pour les documents SPEC.
    Valide la structure, les compteurs de mots et les règles métier spécifiques (ex: EF-<n>).
    """

    # SELF-HEAL: Convert Path to string to match BaseLinter type hints
    TEMPLATE_PATH = str(Path(__file__).resolve().parent.parent / "templates" / "template_spec.docx")
    REQUIREMENT_ID_PATTERN = re.compile(r"\bEF-\d+\b")

    def __init__(self, template_path: Union[str, Path, None] = None):
        # SELF-HEAL: Ensure template_path is cast to string for BaseLinter compatibility
        super().__init__(template_path=str(template_path or self.TEMPLATE_PATH))

    def validate(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Valide un document SPEC complet contre les règles du template et les contraintes métier.
        
        Args:
            document_path: Chemin vers le fichier .docx à valider.
            
        Returns:
            Dictionnaire de rapport de conformité structuré.
        """
        report = super().validate(str(document_path))
        
        # Si le document échoue déjà aux règles de base, on retourne le rapport tel quel.
        if not report.get("valid", False):
            return report

        # Vérification spécifique SPEC : présence d'au moins un ID EF-<n>
        doc = Document(str(document_path))
        req_section_text = self._extract_section_text(doc, "Exigences fonctionnelles")
        
        if req_section_text:
            if not self.REQUIREMENT_ID_PATTERN.search(req_section_text):
                report["valid"] = False
                report.setdefault("spec_violations", []).append(
                    "Aucun identifiant de type 'EF-<n>' trouvé dans la section 'Exigences fonctionnelles'."
                )
        else:
            report.setdefault("spec_violations", []).append(
                "Section 'Exigences fonctionnelles' introuvable ou vide, impossible de valider les identifiants EF-<n>."
            )

        return report

    @staticmethod
    def _extract_section_text(doc: Document, heading: str) -> str:
        """
        Extrait le texte contenu sous un titre spécifique jusqu'au prochain titre de même niveau ou supérieur.
        """
        text_parts = []
        capturing = False
        
        for para in doc.paragraphs:
            # SELF-HEAL: Added null check for para.style to prevent AttributeError
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