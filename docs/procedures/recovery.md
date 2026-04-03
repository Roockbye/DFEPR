# Procédure de Récupération de Fichiers - DFEPR

## Vue d'ensemble

Ce document décrit les procédures de récupération de fichiers supprimés et cachés
à partir d'images disque forensiques, conformément aux directives ACPO.

## Types de Récupération

### 1. Récupération Simple (Fichiers Récemment Supprimés)

**Conditions:**
- Fichier complètement supprimé mais entrée FAT/MFT reste
- Clusters non encore écrasés
- Haute probabilité de succès

**Procédure:**
```bash
# Utiliser The Sleuth Kit (TSK)
istat image.img <inode_number>  # Information sur le fichier
icat image.img <inode_number> > output.bin  # Extraire le fichier
```

### 2. Récupération par Signature (Carving)

**Conditions:**
- Fichier fragmenté ou sans métadonnées
- FAT/MFT écrasé
- Données physiquement présentes

**Procédure:**
```bash
# Utiliser PhotoRec ou Scalpel
photorec /d output_dir /cmd image.img recover
scalpel -o output_dir image.img
```

## Outils Disponibles

### The Sleuth Kit (TSK)

**Avantages:**
- Analyse fs directe
- Récupération par inode
- Haute précision

**Limitations:**
- Nécessite une fs reconnaissable
- Inode range limité
- Pas de carving complet

```bash
# Scan inodes
fls -r image.img

# Informations détaillées
istat image.img <inode>

# Extraire fichier
icat image.img <inode> > recovered_file
```

### PhotoRec

**Avantages:**
- Récupération par signature
- Multi-format
- Rapture haute

**Limitations:**
- Peut créer faux positifs
- Pas d'organisation
- Consommation mémoire

```bash
# Mode ligne de commande
photorec /d output_dir /cmd image.img recover

# Paramètres:
# /d: Directory for output
# /cmd: Use command line interface
# /forensic: Try to extract only unallocated sectors
```

### Scalpel

**Avantages:**
- Configuration flexible
- Haute performance
- Logs détaillés

**Limitations:**
- Nécessite fichier de configuration
- Dépend des signatures
- Ressources importantes

```bash
# Récupérer avec config par défaut
scalpel image.img -o output_dir

# Avec config personnalisé
scalpel -c scalpel.conf image.img -o output_dir
```

## Procédure Complète de Récupération

### Étape 1: Préparer l'environnement

```bash
#!/bin/bash

CASE_ID="THEFT_2026_000001"
IMAGE="/mnt/images/THEFT_2026_000001_001.img"
OUTPUT_DIR="/mnt/recovered/$CASE_ID"

# Créer répertoire
mkdir -p "$OUTPUT_DIR"/{tsk,photorec,scalpel}

# Vérifier l'image
ls -lh "$IMAGE"

# Vérifier l'espace
df -h "$OUTPUT_DIR"
```

### Étape 2: Analyse du Système de Fichiers

```bash
# Déterminer le type de fs
file "$IMAGE"

# Obtenir les statistiques
fsstat "$IMAGE"

# Lister les partitions (si applicable)
parted "$IMAGE" print
```

### Étape 3: Récupération par Inode (TSK)

```bash
#!/bin/bash

IMAGE="/mnt/images/THEFT_2026_000001_001.img"
OUTPUT_DIR="/mnt/recovered/THEFT_2026_000001/tsk"

echo "=== TSK Recovery ==="

# Method 1: List all files (allocated and unallocated)
echo "Listing filesystem..."
fls -r "$IMAGE" > "$OUTPUT_DIR/filelist.txt"

# Method 2: Get statistics
fsstat "$IMAGE" > "$OUTPUT_DIR/fsstat.txt"

# Method 3: Recover specific deleted files
echo "Recovering deleted files..."

# Find deleted files
fls -r -d "$IMAGE" > "$OUTPUT_DIR/deleted_files.txt"

# Extract each deleted file
while read line; do
    INODE=$(echo "$line" | grep -oP '^\s+\d+' | tr -d ' ')
    FILENAME=$(echo "$line" | awk '{print $NF}')
    
    if [ ! -z "$INODE" ]; then
        OUTPUT_FILE="$OUTPUT_DIR/${FILENAME}_inode_${INODE}"
        icat "$IMAGE" "$INODE" > "$OUTPUT_FILE" 2>/dev/null
        
        if [ -s "$OUTPUT_FILE" ]; then
            echo "✓ Recovered: $FILENAME"
        fi
    fi
done < "$OUTPUT_DIR/deleted_files.txt"

echo "TSK recovery complete"
```

### Étape 4: Récupération par Signature (PhotoRec)

```bash
#!/bin/bash

IMAGE="/mnt/images/THEFT_2026_000001_001.img"
OUTPUT_DIR="/mnt/recovered/THEFT_2026_000001/photorec"

echo "=== PhotoRec Recovery ==="

# Run PhotoRec
# Note: This may take a VERY long time for large images
photorec \
    /d "$OUTPUT_DIR" \
    /cmd "$IMAGE" \
    recover

# PhotoRec will create organized directories by file type
ls -la "$OUTPUT_DIR/recycle.bin"

echo "PhotoRec recovery complete"
```

### Étape 5: Récupération Avancée (Scalpel)

```bash
#!/bin/bash

IMAGE="/mnt/images/THEFT_2026_000001_001.img"
OUTPUT_DIR="/mnt/recovered/THEFT_2026_000001/scalpel"
CONFIG="/etc/scalpel/scalpel.conf"

echo "=== Scalpel Recovery ==="

# Create custom config (optional)
cat > "$OUTPUT_DIR/scalpel.conf" << 'EOF'
# Scalpel configuration
# Format: extension [options] image_type [min_size] [max_size]
jpg      Y    1000    500K    2000K
png      Y    1000    500K    2000K
pdf      Y    1000    10M     100M
doc      Y    1000    1M      50M
xls      Y    1000    100K    20M
gz       Y    1000    100K    50M
zip      Y    1000    100K    50M
EOF

# Run Scalpel
scalpel "$IMAGE" \
    -c "$OUTPUT_DIR/scalpel.conf" \
    -o "$OUTPUT_DIR" \
    -v

# Scalpel output organized by filetype
ls -la "$OUTPUT_DIR/audit.txt"

echo "Scalpel recovery complete"
```

### Étape 6: Analyse des Résultats

```bash
#!/bin/bash

RECOVERY_DIR="/mnt/recovered/THEFT_2026_000001"

echo "=== Recovery Summary ==="

# Count recovered files by method
echo "Files recovered:"
echo "  TSK:      $(find $RECOVERY_DIR/tsk -type f | wc -l)"
echo "  PhotoRec: $(find $RECOVERY_DIR/photorec -type f | wc -l)"
echo "  Scalpel:  $(find $RECOVERY_DIR/scalpel -type f | wc -l)"

# List by file type (PhotoRec result)
echo ""
echo "Recovered file types:"
ls -d "$RECOVERY_DIR/photorec/recycle.bin"/* 2>/dev/null | while read dir; do
    TYPE=$(basename "$dir")
    COUNT=$(find "$dir" -type f | wc -l)
    echo "  $TYPE: $COUNT files"
done

# Generate statistics
echo ""
echo "Detailed statistics:"
du -sh "$RECOVERY_DIR"/*
```

## Analyse des Fichiers Récupérés

### Étape 1: Validation des Fichiers

```bash
# Vérifier l'intégrité
file /path/to/recovered_file

# Chercher les signatures
xxd -l 256 /path/to/recovered_file | head

# Pour des images
identify /path/to/recovered_image.jpg
```

### Étape 2: Classification

```bash
# Organiser par type
find /mnt/recovered -type f -exec file {} \; | \
    awk -F: '{print $2}' | sort | uniq -c | sort -rn
```

### Étape 3: Documentation

```markdown
## Recovery Report - THEFT_2026_000001_001

### Summary
- Total Files Recovered: XXX
- By Method:
  - TSK: XXX files (small files, high confidence)
  - PhotoRec: XXX files (medium confidence)
  - Scalpel: XXX files (signature-based)

### Major File Types
- JPEG Images: XXX
- PDF Documents: XXX
- Microsoft Office: XXX

### Notable Findings
- [Description of significant findings]
- [Timestamps of file operations]
- [Patterns in recovered data]

### Confidence Assessment
- High: Files with intact structure and metadata
- Medium: Files recovered by signature matching
- Low: Fragmentary data of uncertain origin

### Chain of Custody
[Standard CoC entry for recovery]
```

## Bonnes Pratiques

### À FAIRE
- ✓ Documenter chaque tentative de récupération
- ✓ Vérifier l'intégrité des fichiers récupérés
- ✓ Conserver les logs de récupération
- ✓ Utiliser plusieurs outils
- ✓ Tester les fichiers avant analyse
- ✓ Archiver les fichiers récupérés

### À NE PAS FAIRE
- ✗ Modifier les fichiers récupérés
- ✗ Analyser sans vérification
- ✗ Abandonner la récupération trop tôt
- ✗ Oublier la documentation
- ✗ Supposer la qualité du fichier
- ✗ Partager les fichiers non documentés

## Limitations

### Fichiers Non Récupérables
- Données écrasées par système d'exploitation
- Fichiers TS fragmentés sans info allocation
- Données chiffrées (impossible à carving)
- Clusters défectueux
- Données compressées sans en-tête

### Facteurs Affectant la Récupération
- Âge de la suppression
- Activité système après suppression
- Fragmentation du disque
- Type de système de fichiers
- Niveau d'usure des secteurs

## Rapport de Récupération

```
RECOVERY EXAMINATION REPORT

Evidence ID: [ID]
Date: [Date]
Examiner: [Name]

SUMMARY:
Total files recovered: [Number]

RECOVERY METHODS USED:
- [Method 1]: [Number] files
- [Method 2]: [Number] files

SIGNIFICANT FINDINGS:
[Description of notable recovered files]

CHAIN OF CUSTODY:
[CoC documentation]

CONCLUSION:
[Professional assessment of recovery quality]

FILES AVAILABLE FOR FURTHER ANALYSIS:
[File list with paths]
```

---

**Document Version:** 1.0
**Last Updated:** 2026-04-03
**ACPO Compliance:** Verified
