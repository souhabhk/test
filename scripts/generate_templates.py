import os
from docx import Document

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

SPEC_HEADINGS = [
    "Introduction",
    "Contexte",
    "Acteurs",
    "Exigences fonctionnelles",
    "Contraintes",
    "Glossaire"
]

SPEC_RULES = [
    ("Introduction", "Oui", 50),
    ("Contexte", "Oui", 100),
    ("Acteurs", "Oui", 30),
    ("Exigences fonctionnelles", "Oui", 200),
    ("Contraintes", "Oui", 50),
    ("Glossaire", "Non", 20),
    ("Total document", "Oui", 500),
]

ARCHI_HEADINGS = [
    "Vue d'ensemble",
    "Composants",
    "Flux de données",
    "Déploiement",
    "Sécurité",
    "Décisions techniques"
]

ARCHI_RULES = [
    ("Vue d'ensemble", "Oui", 80),
    ("Composants", "Oui", 150),
    ("Flux de données", "Oui", 100),
    ("Déploiement", "Oui", 50),
    ("Sécurité", "Oui", 40),
    ("Décisions techniques", "Non", 50),
    ("Total document", "Oui", 600),
]


def create_template(headings: list[str], rules: list[tuple[str, str, int]], output_path: str) -> None:
    """Generates a .docx template with specified headings and validation rules table."""
    doc = Document()
    doc.add_heading("Template de Validation", level=0)

    for heading in headings:
        doc.add_heading(heading, level=1)
        doc.add_paragraph(f"[Contenu pour la section {heading}]")

    doc.add_heading("Règles de validation", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Section"
    hdr_cells[1].text = "Obligatoire"
    hdr_cells[2].text = "Mots minimum"

    for section, mandatory, min_words in rules:
        row_cells = table.add_row().cells
        row_cells[0].text = section
        row_cells[1].text = mandatory
        row_cells[2].text = str(min_words)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"Template généré avec succès : {output_path}")


def main() -> None:
    spec_path = os.path.join(TEMPLATE_DIR, "spec_template.docx")
    archi_path = os.path.join(TEMPLATE_DIR, "archi_template.docx")

    create_template(SPEC_HEADINGS, SPEC_RULES, spec_path)
    create_template(ARCHI_HEADINGS, ARCHI_RULES, archi_path)


if __name__ == "__main__":
    main()