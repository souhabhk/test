# Validation Automatique via Linter Déterministe

Ce projet implémente un pipeline de validation déterministe pour les documents SPEC et Architecture générés par IA. Il utilise des modèles `.docx` éditables par les BA/PO pour définir les règles structurelles et de contenu, et des linters Python pour vérifier la conformité avant la persistance.

## 📦 Installation

1. Installez les dépendances requises :
   ```bash
   pip install python-docx>=0.8.11
   ```

2. Assurez-vous que les modèles de référence sont présents dans `src/templates/`. 
   > **Note :** Les fichiers `template_spec.docx` et `template_archi.docx` fournis sont des scripts générateurs. Exécutez-les une fois pour créer les modèles `.docx` initiaux :
   > ```bash
   > python src/templates/template_spec.docx
   > python src/templates/template_archi.docx
   > ```

## 📝 Guide d'édition des modèles (BA/PO)

Les règles de validation sont stockées directement dans les fichiers `.docx`. Pour modifier les exigences :

1. Ouvrez `template_spec.docx` ou `template_archi.docx` dans Microsoft Word ou LibreOffice.
2. Modifiez les titres en utilisant les styles **Titre 1** (Heading 1).
3. Localisez le tableau "Règles de validation" à la fin du document.
4. Ajustez les colonnes :
   - **Section** : Nom exact du titre attendu.
   - **Obligatoire** : `Oui` ou `Non` (détermine si l'absence bloque la validation).
   - **Mots minimum** : Nombre entier de mots requis pour cette section.
5. **Important** : Ne fusionnez pas de cellules, ne modifiez pas l'ordre des colonnes, et conservez le style de tableau standard (`Table Grid`).

## 🚀 Utilisation API

```python
from src.linters.spec_linter import SpecLinter
from src.linters.archi_linter import ArchiLinter

# Initialisation (les règles sont mises en cache)
spec_linter = SpecLinter()
archi_linter = ArchiLinter()

# Validation d'un document généré
report = spec_linter.validate("output/mon_doc_spec.docx")

if not report["is_valid"]:
    print("❌ Échec de la validation :")
    for section in report["missing_sections"]:
        print(f"  - Section manquante : {section}")
    for violation in report["word_count_violations"]:
        print(f"  - {violation['section']}: {violation['actual']} mots (min: {violation['expected']})")
else:
    print("✅ Document conforme.")
```

## 📊 Format de sortie

Le linter retourne un dictionnaire JSON-compatible :
```json
{
  "is_valid": false,
  "missing_sections": ["Glossaire"],
  "word_count_violations": [
    {"section": "Contexte", "expected": 100, "actual": 62}
  ],
  "total_words": 480,
  "spec_violations": [] 
}
```

## ⚙️ Considérations Techniques
- **Comptage des mots** : Déterministe via regex `\b\w+\b` (ignore ponctuation/espaces multiples).
- **Performance** : Les modèles sont parsés une seule fois et mis en cache par instance de linter.
- **Sécurité** : Lecture seule, pas d'exécution de macros, validation des extensions.