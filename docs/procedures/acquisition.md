# Procédure d'Acquisition d'Images - DFEPR

## Vue d'ensemble

Ce document détaille les procédures d'acquisition d'images disque et de stockage de données
pour le laboratoire de forensique numérique (DFEPR), conformément aux directives ACPO.

## Définition

L'acquisition est le processus de création d'une copie exacte au niveau des bits (bitwise)
d'un dispositif de stockage numérique. Cette copie, appelée "image", remplace le dispositif
original pour tout travail d'analyse futur.

## Principes ACPO

### Principe 1: Protection des données originales
- Ne JAMAIS analyser le dispositif original
- Créer une image exacte pour l'analyse
- Conserver l'original dans un stockage sécurisé
- Vérifier l'intégrité de l'image avec des hashes

### Principe 2: Traçabilité
- Documenter la personne qui acquiert l'image
- Enregistrer la date et l'heure exactes
- Identifier le dispositif d'acquisition
- Conserver tous les logs

### Principe 3: Documentation
- Enregistrer tous les paramètres d'acquisition
- Documenter les erreurs ou problèmes
- Fournir des justifications pour toute action
- Conserver les hash originaux

### Principe 4: Responsabilité
- L'acquisition doit être supervisée
- Les procédures doivent être approuvées
- Un responsable doit valider les résultats
- La chaîne de conservation doit être complète

## Matériel Requis

### Équipement Obligatoire
- **Write-Blocker matériel** - Prévient toute modification du dispositif source
- **Ordinateur d'acquisition** - Système dédié au laboratoire
- **Stockage de destination** - Suffisamment grand pour l'image
- **Devicels d'écriture de contrôle** - Pour valider l'acquisition

### Logiciels Requis
- **ddrescue** - Principal outil d'acquisition avec gestion d'erreurs
- **dd** - Alternative standard Unix
- **md5sum/sha256sum** - Calcul d'empreintes cryptographiques
- **logger** - Enregistrement syslog

### Recommandé
- **Disque dur externe** - Stockage d'images sécurisé
- **Batterie d'alimentation** - Protection contre les coupures
- **Conteneurs antistatiques** - Protection des dispositifs

## Préparation Avant Acquisition

### Audit du laboratoire

Avant chaque acquisition, vérifier:

```bash
# 1. Vérifier les outils disponibles
which ddrescue dd md5sum sha256sum

# 2. Vérifier l'espace disque disponible
df -h /destination

# 3. Vérifier les accès root
whoami  # Doit retourner 'root'

# 4. Vérifier la connectivité
lsblk -f  # Lister les périphériques bloc
fdisk -l   # Lister les disques
```

### Documentation pré-acquisition

Compléter le formulaire pré-acquisition:

```
PRE-ACQUISITION CHECKLIST

Case ID: ________________
Evidence ID: ________________
Examiner: ________________
Date: ________________  Heure: ________________

Équipement:
  [ ] Write-Blocker en place
  [ ] Espace disque suffisant
  [ ] Outils disponibles
  [ ] Destination accessible

Dispositif Source:
  [ ] Physiquement inspecté
  [ ] Numéro de série noté
  [ ] État physique documenté
  [ ] Puissance éteinte avant connexion

Dispositif Destination:
  [ ] Internet déconnecté
  [ ] Disque formaté clerement
  [ ] Espace libre suffisant
  [ ] Montage vérifié

Personnel:
  [ ] Examinateur qualifié identifié
  [ ] Superviseur available
  [ ] Deux personnes présentes (recommandé)

Signature: ________________
```

## Procédure d'Acquisition Pas à Pas

### Étape 1: Préparation physique

```bash
# 1. Mettre le dispositif source HORS TENSION
# 2. Brancher le write-blocker au PC d'acquisition
# 3. Brancher le dispositif source au write-blocker
# 4. ATTENDRE 5 secondes d'initialisation
# 5. Vérifier la détection du dispositif:

lsblk
# Ou
dmesg | tail -20

# Résultat attendu:
# sda : Device of interest (le vôtre peut avoir un autre nom)
```

### Étape 2: Identification du dispositif

```bash
# Obtenir les informations du dispositif
blkid /dev/sda

# Résultat:
# /dev/sda: PTTYPE="dos"

# Obtenir la capacité
blockdev --getsize64 /dev/sda
# Résultat: 1000204886016 (bytes)

# Obtenir le modèle et numéro de série
hdparm -I /dev/sda | grep -E 'Model|Serial'
```

### Étape 3: Imprimer le formulaire d'information du dispositif

```
DEVICE INFORMATION FORM

Case ID: THEFT_2026_000001
Evidence ID: THEFT_2026_000001_001

Timestamp: 2026-04-03 10:15:00 UTC

DISPOSITIF SOURCE:
  Device: /dev/sda
  Model: ST1000DM003-1CH162
  Serial: Z4Y3A2K1
  Capacity: 1000204886016 bytes (931 GiB)
  Interface: SATA
  Condition: Seedy, some corrosion on connector
  Write Status: READ-ONLY (write-blocker active)

WRITE-BLOCKER:
  Model: Tableau T35eu
  Serial: WB-12345
  Status: Connected and active
  Mode: Read-only

HOST SYSTEM:
  Hostname: FORENSICS-01
  OS: Ubuntu 20.04 LTS
  Kernel: 5.4.0-42-generic
  Time: 2026-04-03 10:15 UTC

ACQUISITION PARAMETERS:
  Tool: ddrescue
  Version: 1.25.0
  Block Size: 4096
  Retry Count: 3
  Output File: /mnt/evidence/images/THEFT_2026_000001_001.img

Signature: ________________
```

### Étape 4: Calcul de l'espace requis

```bash
# Déterminer la taille exacte
DEVICE=/dev/sda
SIZE=$(blockdev --getsize64 $DEVICE)
SIZE_GB=$(echo "scale=2; $SIZE / 1024 / 1024 / 1024" | bc)

echo "Taille du device: $SIZE bytes ($SIZE_GB GB)"
echo "Espace requis: ~$SIZE_GB GB + 10% marge"

# Vérifier l'espace disponible
df -h /destination/
```

### Étape 5: Exécution de l'acquisition

```bash
#!/bin/bash
# Script d'acquisition sécurisé

CASE_ID="THEFT_2026_000001"
EVIDENCE_ID="THEFT_2026_000001_001"
DEVICE="/dev/sda"
OUTPUT_DIR="/mnt/evidence/images"
EXAMINER="John Doe"

# Créer le répertoire
mkdir -p "$OUTPUT_DIR"

# Définir le chemin de sortie
OUTPUT="$OUTPUT_DIR/${EVIDENCE_ID}.img"
LOG_FILE="${OUTPUT}.log"

# Exécuter ddrescue
echo "[$(date -u +%Y-%m-%d\ %H:%M:%S)] Starting acquisition..."

sudo ddrescue \
    --verbose \
    --force \
    --direct=on \
    --block-size=4096 \
    --retries=3 \
    --rescue-mode \
    "$DEVICE" \
    "$OUTPUT" \
    "$LOG_FILE"

RESULT=$?

# Documenter le résultat
if [ $RESULT -eq 0 ]; then
    echo "[$(date -u +%Y-%m-%d\ %H:%M:%S)] Acquisition successful"
    logger -t DFEPR "Acquisition succeeded: $EVIDENCE_ID"
else
    echo "[$(date -u +%Y-%m-%d\ %H:%M:%S)] Acquisition failed with code $RESULT"
    logger -t DFEPR "Acquisition failed: $EVIDENCE_ID - Exit code $RESULT"
fi

exit $RESULT
```

### Étape 6: Calcul des hash

```bash
# Attendre que le système de fichiers se stabilise
sleep 5

OUTPUT="/mnt/evidence/images/THEFT_2026_000001_001.img"

# Calculer les hash
echo "Calculating MD5..."
MD5=$(md5sum "$OUTPUT" | awk '{print $1}')
echo "MD5: $MD5"

echo "Calculating SHA-256..."
SHA256=$(sha256sum "$OUTPUT" | awk '{print $1}')
echo "SHA-256: $SHA256"

# Sauvegarder les hash
cat > "${OUTPUT}.hashes" << EOF
HASH VERIFICATION FOR: $(basename "$OUTPUT")
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

MD5:    $MD5
SHA256: $SHA256
EOF

echo "Hashes saved to ${OUTPUT}.hashes"
```

### Étape 7: Vérification de l'acquisition

```bash
# Vérifier l'intégrité
OUTPUT="/mnt/evidence/images/THEFT_2026_000001_001.img"

# 1. Vérifier la taille
ORIGINAL_SIZE=$(blockdev --getsize64 /dev/sda)
IMAGE_SIZE=$(stat --format=%s "$OUTPUT")

echo "Original Device: $ORIGINAL_SIZE bytes"
echo "Image File:      $IMAGE_SIZE bytes"

if [ "$ORIGINAL_SIZE" -eq "$IMAGE_SIZE" ]; then
    echo "✓ Size verification PASSED"
else
    echo "✗ Size verification FAILED"
fi

# 2. Vérifier les mount points (ne doit pas être monté)
if mountpoint -q "$OUTPUT"; then
    echo "✗ Image should NOT be mounted"
else
    echo "✓ Image is not mounted (PASS)"
fi
```

## Post-Acquisition

### Formulaire d'enregistrement

```
ACQUISITION COMPLETION REPORT

Case ID: THEFT_2026_000001
Evidence ID: THEFT_2026_000001_001

ACQUISITION DETAILS:
  Date/Time Start: 2026-04-03 10:15:00 UTC
  Date/Time End:   2026-04-03 10:45:00 UTC
  Duration: 30 minutes
  
  Device Source: /dev/sda (ST1000DM003)
  Output File: /mnt/evidence/images/THEFT_2026_000001_001.img
  File Size: 1000204886016 bytes
  
  Status: ✓ SUCCESSFUL

HASH VERIFICATION:
  MD5:    a1b2c3d4e5f6g7h8i9j0
  SHA256: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
  
  [ ] Hashes match expected values
  [ ] Hash file archived

CHAIN OF CUSTODY:
  Acquirer: John Doe
  Signature: ________________  Date: ________________
  
  Supervisor: Jane Smith
  Signature: ________________  Date: ________________

ISSUES/NOTES:
  None

NEXT STEPS:
  [ ] Store original device in secure location
  [ ] Archive image to backup storage
  [ ] Begin analysis (if required)
  [ ] Update case file
```

### Stockage de l'image

```bash
# 1. Copier vers stockage secondaire (recommandé)
cp /mnt/evidence/images/THEFT_2026_000001_001.img /backup/images/

# 2. Vérifier l'intégrité de la copie
md5sum /mnt/evidence/images/THEFT_2026_000001_001.img > original.md5
md5sum /backup/images/THEFT_2026_000001_001.img > backup.md5

if diff original.md5 backup.md5; then
    echo "✓ Backup verification PASSED"
else
    echo "✗ Backup verification FAILED"
fi

# 3. Faire de la archive sécurisée
# - Chiffrer (recommandé)
# - Stocker hors-site (recommandé)
# - Documenter l'emplacement
```

## Dépannage

### Erreur: Device non reconnu

```bash
# Solution 1: Attendre l'initialisation USB
sleep 10
lsblk

# Solution 2: Redémarrer le write-blocker
# Débrancher et rebrancher le connecteur USB

# Solution 3: Vérifier les pilotes
lsusb
modprobe usb-storage

# Solution 4: Vérifier avec le journal
dmesg | grep -i scsi
```

### Erreur: Permission refusée

```bash
# Vérifier l'ID utilisateur
whoami  # Doit être 'root'

# Sinon utiliser sudo
sudo ddrescue [options]

# Ou ajouter à sudoers
sudo visudo
# Ajouter: forensics ALL=(ALL) NOPASSWD: /usr/bin/ddrescue
```

### Erreur: Espace disque insuffisant

```bash
# Vérifier l'espace
df -h /destination

# Nettoyer l'espace disque
rm -f /destination/*.tmp

# Utiliser une destination alternative
ddrescue /dev/sda /alternate/path/image.img image.log
```

## Checklist Finale

Before analyzing acquired image, complete:

- [ ] Image file size matches original device
- [ ] MD5 and SHA-256 hashes calculated and verified
- [ ] Original device stored in secure location
- [ ] Acquisition log reviewed for errors
- [ ] Chain of custody documentation complete
- [ ] Metadata file created and stamped
- [ ] Backup copy verified
- [ ] Case file updated
- [ ] All personnel signed off
- [ ] Ready to proceed with analysis

---

**Document Version:** 1.0
**Last Updated:** 2026-04-03
**ACPO Compliance:** Verified
