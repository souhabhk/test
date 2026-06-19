import os
from docx import Document

def create_template(output_path: str, headings: list[str], rules: list[tuple[str, str, int]]) -> None:
    """Generate a .docx template with specified headings and a validation rules table."""
    doc = Document()
    
    # Add expected section headings using standard Word styles
    for heading in headings:
        doc.add_heading(heading, level=1)
        
    # Add validation rules table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # Configure header row
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Section'
    header_cells[1].text = 'Obligatoire'
    header_cells[2].text = 'Mots minimum'
    
    # Populate data rows
    for section_name, mandatory, min_words in rules:
        row_cells = table.add_row().cells
        row_cells[0].text = section_name
        row_cells[1].text = mandatory
        row_cells[2].text = str(min_words)
        
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    doc.save(output_path)
    print(f"✅ Template generated: {output_path}")

def main() -> None:
    # SPEC Configuration
    spec_headings = [
        "Introduction",
        "Contexte",
        "Acteurs",
        "Exigences fonctionnelles",
        "Contraintes",
        "Glossaire"
    ]
    spec_rules = [
        ("Introduction", "Oui", 50),
        ("Contexte", "Oui", 100),
        ("Acteurs", "Oui", 30),
        ("Exigences fonctionnelles", "Oui", 200),
        ("Contraintes", "Oui", 50),
        ("Glossaire", "Non", 20),
        ("Total document", "Oui", 500)
    ]
    
    # Architecture Configuration
    archi_headings = [
        "Vue d'ensemble",
        "Composants",
        "Flux de données",
        "Déploiement",
        "Sécurité",
        "Décisions techniques (ADR)"
    ]
    archi_rules = [
        ("Vue d'ensemble", "Oui", 80),
        ("Composants", "Oui", 150),
        ("Flux de données", "Oui", 100),
        ("Déploiement", "Oui", 50),
        ("Sécurité", "Oui", 40),
        ("Décisions techniques", "Non", 50),
        ("Total document", "Oui", 600)
    ]
    
    create_template("templates/spec_template.docx", spec_headings, spec_rules)
    create_template("templates/archi_template.docx", archi_headings, archi_rules)

if __name__ == "__main__":
    main()
