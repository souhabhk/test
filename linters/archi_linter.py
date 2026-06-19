import re
from typing import Dict, List, Any

# SELF-HEAL: Use relative import to match package structure
from .base_linter import BaseDocumentLinter, ValidationReport


class ArchiLinter(BaseDocumentLinter):
    """
    Linter déterministe pour les documents d'Architecture.
    Valide la structure via le template et applique des règles métier spécifiques 
    (détail des composants, flux de données, ADR).
    """
    
    # Mots-clés déterministes pour vérifier le détail des composants
    COMPONENT_KEYWORDS = [
        "responsabilité", "responsabilite",
        "technologie", "technologies",
        "tech stack", "stack technique",
        "implémente", "fournit", "expose", "interface"
    ]
    
    def __init__(self, template_path: str):
        super().__init__(template_path)
        
    def validate_structure(self, target_doc_path: str) -> ValidationReport:
        # SELF-HEAL: Removed duplicate local ValidationReport definition and dict/object fallback logic.
        # Now correctly inherits and extends the base report.
        report = super().validate_structure(target_doc_path)
        
        # Extraction des sections pour les vérifications métier
        sections = self.extract_sections(target_doc_path)
        
        # Vérification spécifique : Composants
        composants_paragraphs = sections.get("Composants", [])
        if composants_paragraphs:
            self._check_composants(composants_paragraphs, report)
            
        # Vérification spécifique : Flux de données
        flux_paragraphs = sections.get("Flux de données", [])
        if flux_paragraphs:
            self._check_flux(flux_paragraphs, report)
            
        # Vérification spécifique : Décisions techniques (ADR)
        adr_paragraphs = sections.get("Décisions techniques", [])
        if adr_paragraphs:
            self._check_adr(adr_paragraphs, report)
            
        return report

    def _get_section_text(self, paragraphs) -> str:
        """Concatène le texte des paragraphes en ignorant les vides."""
        return " ".join(p.text for p in paragraphs if hasattr(p, 'text') and p.text.strip())

    def _check_composants(self, paragraphs, report: ValidationReport):
        """
        Vérifie que la section Composants contient au moins un composant détaillé 
        (responsabilité + technologie).
        """
        text = self._get_section_text(paragraphs).lower()
        matched = [kw for kw in self.COMPONENT_KEYWORDS if kw.lower() in text]
        
        if not matched:
            report.add_issue(
                section="Composants",
                rule="component_details",
                message="La section 'Composants' doit détailler au moins un composant avec sa responsabilité et sa technologie."
            )
        elif len(matched) < 2:
            report.add_issue(
                section="Composants",
                rule="component_details_warning",
                message=f"La section 'Composants' manque de détails techniques. Mots-clés détectés: {', '.join(matched)}."
            )

    def _check_flux(self, paragraphs, report: ValidationReport):
        """
        Vérifie la présence d'indicateurs de flux de données.
        """
        text = self._get_section_text(paragraphs).lower()
        indicators = ["source", "destination", "déclencheur", "trigger", "message", "payload", "données"]
        found = [ind for ind in indicators if ind in text]
        
        if not found:
            report.add_issue(
                section="Flux de données",
                rule="flux_indicators",
                message="La section 'Flux de données' ne contient pas d'indicateurs standards (source, destination, message, etc.)."
            )

    def _check_adr(self, paragraphs, report: ValidationReport):
        """
        Vérifie la structure des ADR (Architecture Decision Records).
        """
        text = self._get_section_text(paragraphs)
        # Recherche d'identifiants ADR ou de mots-clés structurels
        pattern = r'\b(ADR-?\d+|DÉCISION|DECISION|CONTEXT|CONTEXTE|CONCLUSION|STATUS)\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if not matches:
            report.add_issue(
                section="Décisions techniques",
                rule="adr_format",
                message="La section 'Décisions techniques' ne respecte pas le format ADR standard."
            )