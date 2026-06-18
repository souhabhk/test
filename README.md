# Validation Automatique via Linter Déterministe

Ce projet implémente un pipeline de validation déterministe pour les documents SPEC et Architecture générés par IA. Il utilise des modèles `.docx` éditables par les BA/PO pour définir les règles structurelles, et des linters dédiés pour vérifier la conformité avant la persistance.

## Installation

Assurez-vous d'avoir Python 3.8+ installé. Installez les dépendances requises :

```bash
pip install python-docx>=0.8.11
```

## Guide d'édition des modèles (BA/PO)

Les règles de validation sont stockées dans `src/templates/template_spec.docx` et `src/templates/template_archi.docx`. Pour modifier les exigences :

1. Ouvrez le modèle dans Microsoft Word ou LibreOffice.
2. Modifiez les titres en utilisant les styles standard "Titre 1", "Titre 2", etc.
3. Localisez le tableau de règles à la fin du document. Il doit respecter strictement ce format :
   | Section | Obligatoire | Mots minimum |
   |---|---|---|
   | Introduction | Oui | 50 |
4. **Important** : Ne fusionnez pas de cellules, n'utilisez pas de tableaux imbriqués, et conservez l'ordre des colonnes. Les valeurs "Oui"/"Non" (ou Yes/No) sont interprétées automatiquement.

## Utilisation de l'API de validation

Les linters sont conçus pour être intégrés dans le cycle de génération IA. Ils retournent un rapport JSON structuré permettant des boucles de correction déterministes.

### Exemple SPEC

```python
from src.linters.spec_linter import SpecLinter

linter = SpecLinter()
report = linter.validate("path/to/generated_spec.docx")

if not report["valid"]:
    print(f"Validation échouée: {report['missing_sections']}")
    # Retourner le rapport à l'agent IA pour ajustement du prompt
```

### Exemple Architecture

```python
from src.linters.archi_linter import ArchiLinter

linter = ArchiLinter()
report = linter.validate("path/to/archi_doc.docx")
```

## Structure du rapport de validation

Le linter retourne un dictionnaire contenant :
- `valid` (bool) : `True` si le document respecte toutes les règles.
- `missing_sections` (list) : Titres obligatoires absents.
- `word_count_violations` (list) : Sections ne respectant pas le nombre minimum de mots.
- `total_words` (int) : Nombre total de mots dans le document.
- `section_counts` (dict) : Comptage des mots par section.
- *(Optionnel)* `requirement_id_violations` / `archi_specific_violations` : Erreurs spécifiques au type de document.

## Considérations techniques
- **Comptage déterministe** : Utilise l'expression régulière `\b\w+\b` pour ignorer la ponctuation et les sauts de ligne.
- **Performance** : Les règles du modèle sont mises en cache après le premier chargement.
- **Sécurité** : Les fichiers `.docx` sont traités en lecture seule. Aucune macro n'est exécutée.