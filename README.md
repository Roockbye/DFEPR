# Digital Forensics Evidence Preservation & Recovery Lab (DFEPR)

Laboratoire simulé d'investigation en forensique numérique utilisant des outils open-source pour l'acquisition d'images disque, la récupération de fichiers supprimés et la production de rapports de preuves admissibles en cour, conformément aux directives ACPO (Association of Chief Police Officers).

## Objectifs

- 📋 Acquisition sécurisée d'images disque avec vérification d'intégrité
- 🔍 Récupération de fichiers supprimés et fragments de données
- 📊 Production de rapports de preuves numériques admissibles en cour
- 🔐 Chaîne de conservation complète et traçabilité
- 📝 Documentation exhaustive des procédures et méthodologies

## Caractéristiques principales

### 1. Acquisition d'Images Disque
- Support pour imaging disque brut (dd, ddrescue)
- Calcul d'empreintes cryptographiques (MD5, SHA256)
- Gestion des erreurs de lecture secteur
- Consolidation d'images fragmentées

### 2. Récupération de Données
- Utilisation de The Sleuth Kit (TSK)
- Récupération de fichiers supprimés
- Analyse de clusters FAT
- Support multi-systèmes de fichiers (NTFS, ext4, FAT32, etc.)

### 3. Chaîne de Conservation
- Logging automatique des opérations
- Empreintes cryptographiques de tous les fichiers
- Métadonnées de preuve
- Rapport d'investigation

### 4. Rapports Admissibles en Cour
- Format PDF conforme aux exigences légales
- Résumé exécutif
- Méthodologie détaillée
- Résultats et conclusion
- Annexes techniques

## Structure du Projet

```
DFEPR/
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── setup.sh
├── config/
│   ├── evidence_templates.json
│   ├── acpo_guidelines.md
│   └── hash_algorithms.ini
├── scripts/
│   ├── acquire_image.sh
│   ├── verify_integrity.sh
│   ├── recover_deleted_files.sh
│   └── generate_report.py
├── src/
│   ├── evidence_tracker.py
│   ├── hash_verifier.py
│   ├── file_recovery.py
│   ├── report_generator.py
│   └── chain_of_custody.py
├── evidence/
│   ├── cases/
│   ├── images/
│   ├── recovered/
│   └── reports/
├── docs/
│   ├── ACPO_Guidelines.md
│   ├── procedures/
│   └── case_examples/
└── tests/
    └── test_*.py
```

## Directives ACPO

Les principes fondamentaux ACPO pour la préservation des preuves:

1. **Principe 1**: Pas d'action ne doit modifier les données originales
2. **Principe 2**: Les personnes accédant aux preuves doivent être nommées
3. **Principe 3**: Procédures de transmission et de manipulation documentées
4. **Principe 4**: Responsable du laboratoire doit une personne senior

Voir `docs/ACPO_Guidelines.md` pour détails complets.

## Outils Utilisés

- **ddrescue** - Acquisition d'images avec gestion d'erreurs
- **The Sleuth Kit (TSK)** - Analyse de systèmes de fichiers
- **PhotoRec/Scalpel** - Récupération de fichiers
- **OpenSSL** - Calcul d'empreintes cryptographiques
- **Python 3** - Scripts d'automatisation et reporting

## Installation

```bash
./setup.sh
```

## Utilisation Rapide

### Acquérir une image disque

```bash
./scripts/acquire_image.sh /dev/sdX /path/to/output.img
```

### Vérifier l'intégrité

```bash
./scripts/verify_integrity.sh /path/to/image.img
```

### Récupérer des fichiers supprimés

```bash
./scripts/recover_deleted_files.sh /path/to/image.img /output/recovery/
```

### Générer un rapport

```bash
python3 scripts/generate_report.py --case-id CASE_001 --output report.pdf
```

## Documentation

- [Directives ACPO](docs/ACPO_Guidelines.md)
- [Procédures d'Acquisition](docs/procedures/acquisition.md)
- [Procédures de Récupération](docs/procedures/recovery.md)
- [Chaîne de Conservation](docs/procedures/chain_of_custody.md)

## Contribution

Pour contribuer au projet, veuillez respecter les directives ACPO et documentez toutes les modifications.

## Licence

À définir selon la juridiction locale

## Auteur

Créé pour des fins éducatives et d'investigation légale

---

**Disclaimer**: Ce laboratoire est destiné à des fins éducatives et d'investigation autorisée uniquement. 
L'accès non autorisé aux données d'autrui est illégal.
