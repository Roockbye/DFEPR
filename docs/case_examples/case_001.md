# Exemple de Cas Complet - DFEPR

## Scénario

**Titre**: Enquête sur Vol de Données - ABC Corporation

**Résumé**: ABC Corporation rapporte le vol de données sensibles. Une enquête interne 
a identifié un ancien employé ayant accés aux serveurs avant son départ. 
L'objectif: acquérir et analyser son ordinateur portable personnel pour détecter 
l'accès non autorisé à des données confidentielles.

## Détails du Cas

```
Case ID:             DATATHEFT_2026_000001
Evidence ID:         DATATHEFT_2026_000001_001
Incident Date:       2026-03-15
Report Date:         2026-04-03
Case Officer:        Detective Jane Smith
Reporting Agency:    Metropolitan Police - Cybercrime Unit
Suspect:             Robert Johnson (Former IT Manager)
Victim:              ABC Corporation
```

## Étape 1: Acquisition de l'Image Disque

### Préparation

```bash
# Vérifier les outils
which ddrescue md5sum sha256sum

# Préparer l'espace
mkdir -p /mnt/evidence/images/DATATHEFT_2026_000001
df -h /mnt/evidence/

# Préparer les logs
LOG_DIR="evidence/cases/DATATHEFT_2026_000001"
mkdir -p "$LOG_DIR"
```

### Acquisition

**Date/Heure**: 2026-04-03 10:15:00 UTC
**Examinateur**: John Doe (Senior Forensic Examiner, 12 years experience)
**Superviseur**: Jane Smith (Lab Manager)

```bash
# Connecter le dispositif avec write-blocker
# Device reconnu: /dev/sda
# Modèle: Lenovo ThinkPad (128GB SSD)
# Numéro de série: PF-0ABC123XY

blockdev --getsize64 /dev/sda
# Output: 128035676160 bytes

# Exécuter l'acquisition
sudo ddrescue \
    --verbose \
    --force \
    --direct=on \
    --block-size=4096 \
    --retries=3 \
    /dev/sda \
    /mnt/evidence/images/DATATHEFT_2026_000001/laptop.img \
    /mnt/evidence/images/DATATHEFT_2026_000001/laptop.log

# Durée: 45 minutes
# Erreurs: 0
# Status: SUCCESS
```

### Vérification de l'Intégrité

```bash
IMAGE="/mnt/evidence/images/DATATHEFT_2026_000001/laptop.img"

# Vérifier la taille
ls -lh "$IMAGE"
# -rw-r--r-- 1 root root 119G Apr  3 10:59 laptop.img

# Calculer les hashes
MD5=$(md5sum "$IMAGE" | awk '{print $1}')
SHA256=$(sha256sum "$IMAGE" | awk '{print $1}')

echo "MD5:    $MD5"
echo "SHA256: $SHA256"

# Sauvegarder les hashes
cat > "${IMAGE}.hashes" << EOF
Hash Verification for: laptop.img
Generated: 2026-04-03 11:04:00 UTC

MD5:    $MD5
SHA256: $SHA256

Verified by: John Doe
Date: 2026-04-03
EOF
```

## Étape 2: Chaîne de Custody

### Entrée d'Acquisition

```python
from src.chain_of_custody import ChainOfCustody, CustodyAction
from datetime import datetime

coc = ChainOfCustody("DATATHEFT_2026_000001", "DATATHEFT_2026_000001_001")

coc.add_entry(
    action=CustodyAction.ACQUISITION,
    person_name="John Doe",
    person_title="Senior Forensic Examiner",
    location="Digital Lab - Building A, Room 101",
    description="Bitwise acquisition of Lenovo ThinkPad laptop using ddrescue",
    items_affected=[
        "/dev/sda - Lenovo ThinkPad 128GB SSD",
        "laptop.img - Image file 119GB"
    ],
    signature="JD-20260403-001",
    notes="Device connected via Tableau T35eu write-blocker. Zero errors during acquisition."
)

# Générer le rapport
report_text = coc.generate_report()
print(report_text)
```

### Export pour Documentation

```bash
python3 << 'EOF'
from src.chain_of_custody import ChainOfCustody

coc = ChainOfCustody("DATATHEFT_2026_000001", "DATATHEFT_2026_000001_001")
coc.export_for_submission("evidence/cases/DATATHEFT_2026_000001/coc_report_001.txt")
print("Chain of Custody report exported")
EOF
```

## Étape 3: Récupération de Fichiers Supprimés

### Récupération par Signature (PhotoRec)

```bash
# Lancer PhotoRec
IMAGE="/mnt/evidence/images/DATATHEFT_2026_000001/laptop.img"
OUTPUT_DIR="/mnt/evidence/recovered/DATATHEFT_2026_000001"

mkdir -p "$OUTPUT_DIR"

# Note: PhotoRec peut prendre plusieurs heures
photorec \
    /d "$OUTPUT_DIR" \
    /cmd "$IMAGE" \
    recover

# Résultats:
# - Total recovered files: 12,847
# - JPEG images: 3,421
# - PDF documents: 287
# - Microsoft Office: 1,892
# - Text files: 2,145
# - Other: 5,102
```

### Analyse des Résultats

```bash
# Compter les fichiers par type
find "$OUTPUT_DIR/photorec/recycle.bin" -type d | head -10

# Exemple output:
# - jpg: 3421 files
# - zip: 456 files
# - xls: 234 files
# - doc: 892 files
# - pdf: 287 files
# - txt: 2145 files
```

## Étape 4: Analyse Forense

### Entrée d'Analyse dans la CoC

```python
from src.chain_of_custody import ChainOfCustody, CustodyAction

coc = ChainOfCustody("DATATHEFT_2026_000001", "DATATHEFT_2026_000001_001")

# Charger les entrées existantes
# (en production, coc chargerait depuis le fichier)

coc.add_entry(
    action=CustodyAction.ANALYSIS,
    person_name="Sarah Wilson",
    person_title="Senior Data Analyst",
    location="Digital Lab - Room 102",
    description="Initial forensic analysis - file recovery and classification",
    items_affected=[
        "DATATHEFT_2026_000001_001",
        "Recovered files: 12,847 items"
    ],
    signature="SW-20260403-002",
    notes="Recovered 12,847 files from unallocated space. Identified 287 PDF files potentially containing company data."
)

coc.add_entry(
    action=CustodyAction.ANALYSIS,
    person_name="Michael Brown",
    person_title="Cybercrime Specialist",
    location="Digital Lab - Room 103",
    description="Deep analysis - data extraction and timeline construction",
    items_affected=[
        "Recovered files: 287 PDFs",
        "Microsoft Office: 1,892 documents",
        "Timeline data"
    ],
    signature="MB-20260403-003",
    notes="Confirmed presence of 23 proprietary ABC Corp documents dated March 2-14, establishing probable unauthorized access."
)
```

## Étape 5: Génération de Rapport

### Données du Rapport

```python
from src.report_generator import ReportGenerator, InvestigationReport, CaseInfo
from datetime import datetime

case_info = CaseInfo(
    case_id="DATATHEFT_2026_000001",
    case_name="ABC Corporation Data Theft Investigation",
    reporting_agency="Metropolitan Police - Cybercrime Unit",
    case_officer="Detective Jane Smith",
    incident_date="2026-03-15",
    report_date="2026-04-03"
)

report = InvestigationReport(
    case_info=case_info,
    evidence_id="DATATHEFT_2026_000001_001",
    examiner_name="John Doe",
    examiner_title="Senior Forensic Examiner",
    examination_date="2026-04-03",
    methodology="""
    1. Bitwise imaging of Lenovo ThinkPad using ddrescue with write-blocking device
    2. Hash verification (MD5 and SHA-256) to ensure integrity
    3. File recovery from unallocated space using PhotoRec
    4. File classification and analysis
    5. Timeline construction from file metadata
    6. Correlation with known ABC Corp document signatures
    7. Chain of custody maintained throughout
    """,
    findings="""
    The analysis revealed extensive evidence of unauthorized data access:
    
    - 287 PDF documents identified as proprietary ABC Corp materials
    - Files dated March 2-14, 2026, corresponding to suspect's employment period
    - Document metadata indicates prints and views by suspect user account
    - 23 highly sensitive documents containing trade secrets identified
    - Email communications recovered indicating knowledge of unauthorized access
    - Deleted file recovery shows deliberate attempt to cover tracks
    - Timeline analysis shows focused extraction of specific departments
    """,
    conclusions="""
    Based on the forensic analysis, there is strong evidence that:
    
    1. The suspect obtained unauthorized access to ABC Corp proprietary data
    2. The data was deliberately extracted from company systems
    3. Attempts were made to cover tracks by deleting files
    4. The recovered data includes highly sensitive trade secrets
    5. The suspect had advanced knowledge of company security
    
    This evidence is admissible in court and demonstrates probable cause
    for prosecution under applicable computer fraud and theft statutes.
    """,
    chain_of_custody_file="evidence/cases/DATATHEFT_2026_000001/coc_report.txt",
    hash_verification_file="evidence/cases/DATATHEFT_2026_000001/hashes.json"
)

generator = ReportGenerator("DATATHEFT_2026_000001")
text_report = generator.save_report(report, format="text")
html_report = generator.save_report(report, format="html")

print(f"Text Report: {text_report}")
print(f"HTML Report: {html_report}")
```

## Étape 6: Documentation Finale

### Résumé de l'Enquête

```
INVESTIGATION SUMMARY
=====================

Case: DATATHEFT_2026_000001
Subject: Robert Johnson (Former IT Manager)
Victim: ABC Corporation

KEY EVIDENCE:
1. Lenovo ThinkPad laptop (PRIMARY)
   - Image: 119GB
   - Files recovered: 12,847
   - Significant findings: 287 proprietary documents

2. Chain of Custody:
   - 3 entries documented
   - All authorized personnel identified
   - Hashes verified at each step
   - ACPO compliant

3. Forensic Findings:
   - 23 sensitive ABC Corp documents
   - Email communications confirming knowledge
   - Timeline matching suspect activity
   - Metadata traces
   - Deleted file recovery evidence

ADMISSIBILITY:
✓ ACPO Guidelines followed
✓ Chain of custody intact
✓ Hash verification passed
✓ Procedures documented
✓ Expert qualifications verified
✓ Court-ready documentation

STATUS: READY FOR PROSECUTION
```

## Fichiers Générés

```
evidence/cases/DATATHEFT_2026_000001/
├── acquisition.txt              # Formulaire d'acquisition
├── coc_complete.json            # Chaîne de custody complète
├── coc_report.txt              # Rapport CoC formaté
├── findings.txt                # Résultats analysés
├── timeline.json               # Timeline des événements
├── hash_verification.json      # Vérification des hashes
└── DATATHEFT_2026_000001.log  # Log consolidé

evidence/images/DATATHEFT_2026_000001/
├── laptop.img                  # Image disque (119GB)
├── laptop.img.hashes          # Fichier des hashes
├── laptop.img.metadata        # Métadonnées image
└── laptop.log                 # Log ddrescue

evidence/recovered/DATATHEFT_2026_000001/
├── photorec/                  # Fichiers récupérés
│   ├── recycle.bin/
│   │   ├── jpg/              # 3,421 images
│   │   ├── pdf/              # 287 documents
│   │   ├── doc/              # 892 documents Office
│   │   └── ...
│   └── audit.txt

evidence/reports/DATATHEFT_2026_000001/
├── investigation_report.txt   # Rapport texte
├── investigation_report.html  # Rapport HTML
└── investigation_report.json  # Rapport JSON
```

## Conclusion

Le cas DATATHEFT_2026_000001 démontre une enquête forensique complète et conforme 
aux directives ACPO, aboutissant à des preuves admissibles en cour et soutenant 
la poursuite pénale contre le suspect.

---

**Cas créé pour**: Démonstration du laboratoire DFEPR
**Date**: 2026-04-03
**Status**: Exemple didactique - Pas de vraies données
