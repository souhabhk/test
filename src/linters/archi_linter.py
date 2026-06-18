import os
from typing import Dict, Any, Optional, Union
from pathlib import Path

from docx import Document
from .base_linter import BaseLinter


class ArchiLinter(BaseLinter):
    """
    Linter déterministe pour les documents d'Architecture.
    Valide la conformité structurelle et le respect des règles définies dans template_archi.docx.
    """

    def __init__(self, template_path: Optional[str] = None):
        if template_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_dir, "..", "templates", "template_archi.docx")
        super().__init__(template_path)

    def validate(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Exécute la validation complète du document Architecture.
        
        Args:
            document_path: Chemin vers le fichier .docx à valider.
            
        Returns:
            Rapport de validation structuré contenant valid, missing_sections, 
            word_count_violations, total_words et archi_specific_violations.
        """
        report = super().validate(str(document_path))
        
        # Si la validation de base échoue, on retourne immédiatement le rapport
        if not report["valid"]:
            return report

        # Validation spécifique Architecture :
        # La section "Composants" doit contenir au moins un composant détaillé
        # mentionnant explicitement sa responsabilité et sa technologie.
        try:
            doc = Document(str(document_path))
            # SELF-HEAL: Replaced undefined self._parsed_headings check with direct document parsing and inherited helper
            components_text = self._extract_section_text(doc, "Composants")
            if components_text:
                lower_text = components_text.lower()
                has_responsability = "responsabilité" in lower_text or "responsabilite" in lower_text
                has_technology = "technologie" in lower_text or "technology" in lower_text
                
                if not (has_responsability and has_technology):
                    report.setdefault("archi_specific_violations", []).append(
                        "La section 'Composants' doit inclure au moins un composant "
                        "précisant sa responsabilité et sa technologie."
                    )
                    report["valid"] = False
        except Exception as e:
            report.setdefault("archi_specific_violations", []).append(f"Error checking components: {e}")
            report["valid"] = False
        
        return report