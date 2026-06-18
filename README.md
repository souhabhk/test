# Validation Automatique via Linter Déterministe

Ce projet implémente un pipeline de validation déterministe pour les documents SPEC et Architecture générés par IA. Il utilise des templates `.docx` éditables par les BA/PO pour définir les règles structurelles, et des linters dédiés pour vérifier la conformité avant la persistance.

## Installation

Assurez-vous d'avoir Python 3.8+ installé. Installez les dépendances requises :

```bash
pip install -r requirements.txt
# ou directement :
pip install python-docx>=0.8.11
```

## Guide d'édition des Templates (BA/PO)

Les règles de validation sont stockées dans `src/templates/template_spec.docx` et `src/templates/template_archi.docx`. Pour maintenir la compatibilité avec le parser automatique, veuillez respecter les consignes suivantes lors de l'édition :

1. **Styles de Titres** : Utilisez exclusivement les styles "Titre 1" (Heading 1) pour les sections principales.
2. **Tableau de Règles** : Chaque template doit contenir un tableau à 3 colonnes avec les en-têtes exactes : `Section | Obligatoire | Mots minimum`.
3. **Structure du Tableau** : Évitez les cellules fusionnées, les tableaux imbriqués ou les styles personnalisés complexes dans ce tableau.
4. **Valeurs** : 
   - `Obligatoire` : Utilisez "Oui" ou "Non".
   - `Mots minimum` : Entier positif (ex: `50`).
   - Ajoutez toujours une ligne `Total document | Oui | <valeur>` pour la validation globale.

## Utilisation de l'API de Validation

Les linters sont conçus pour être instantanés et retourner un rapport structuré JSON/dict pour faciliter les boucles de retry des agents IA.

### Exemple d'utilisation

```python
from src.linters.spec_linter import SpecLinter
from src.linters.archi_linter import ArchiLinter

# Initialisation (les règles du template sont mises en cache)
spec_linter = SpecLinter()
archi_linter = ArchiLinter()

# Validation d'un document généré
report = spec_linter.validate("path/to/generated_spec.docx")

if not report["valid"]:
    print(f"Validation échouée: {report['missing_sections']}")
    print(f"Violations de mots: {report['word_count_violations']}")
else:
    print("Document conforme.")
```

### Structure du Rapport

```json
{
  "valid": false,
  "missing_sections": ["Glossaire"],
  "word_count_violations": [
    {"section": "Contexte", "expected": 100, "actual": 62}
  ],
  "total_words": 480,
  "errors": []
}
```

## Considérations Techniques
- **Comptage des mots** : Déterministe via regex `\b\w+\b` pour ignorer la ponctuation et les espaces multiples.
- **Performance** : Les templates sont parsés une seule fois par instance de linter.
- **Sécurité** : Les fichiers `.docx` sont lus en mode lecture seule sans exécution de macros.