#!/bin/bash

################################################################################
# DFEPR - Image Acquisition Script
# Acquires a bitwise image of a storage device following ACPO guidelines
# Usage: ./acquire_image.sh <source_device> <output_path> [case_id] [examiner]
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HASH_ALGORITHM="sha256"
LOG_DIR="evidence/cases"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function: Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function: Check prerequisites
check_prerequisites() {
    print_info "Vérification des prérequis..."
    
    local required_tools=("ddrescue" "md5sum" "sha256sum" "blockdev" "logger")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool n'est pas installé"
            return 1
        fi
    done
    
    print_success "Tous les prérequis sont satisfaits"
    return 0
}

# Function: Validate device
validate_device() {
    local device=$1
    
    if [ ! -b "$device" ]; then
        print_error "Device $device n'existe pas ou n'est pas un périphérique bloc"
        return 1
    fi
    
    # Check if device is mounted
    if mountpoint -q "$device" 2>/dev/null; then
        print_error "Le device $device est monté. Veuillez le démonter d'abord."
        return 1
    fi
    
    print_success "Device validé: $device"
    return 0
}

# Function: Get device information
get_device_info() {
    local device=$1
    
    print_info "Collecte des informations sur le device..."
    
    local size=$(blockdev --getsize64 "$device")
    local model=$(lsblk -d -n -o MODEL "$device" 2>/dev/null | tr -d ' ')
    local serial=$(lsblk -d -n -o SERIAL "$device" 2>/dev/null | tr -d ' ')
    
    print_info "  Modèle: $model"
    print_info "  Numéro de série: $serial"
    print_info "  Taille: $(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo $size bytes)"
    
    # Return as associative array (bash 4+)
    echo "$model|$serial|$size"
}

# Function: Acquire image using ddrescue
acquire_image() {
    local source=$1
    local output=$2
    local case_id=$3
    
    print_info "Démarrage de l'acquisition d'image bitwise..."
    print_info "Source: $source"
    print_info "Sortie: $output"
    
    # Create output directory
    mkdir -p "$(dirname "$output")"
    
    # Check free space
    local device_info=$(get_device_info "$source")
    IFS='|' read -r model serial size <<< "$device_info"
    local free_space=$(df "$(dirname "$output")" | awk 'NR==2 {print $4}')
    local free_bytes=$((free_space * 1024))
    
    if (( free_bytes < size )); then
        print_error "Espace insuffisant. Requis: $(numfmt --to=iec-i --suffix=B $size 2>/dev/null) Disponible: $(numfmt --to=iec-i --suffix=B $free_bytes 2>/dev/null)"
        return 1
    fi
    
    # Run ddrescue with logging
    local log_file="${output}.log"
    print_info "Lancement de ddrescue (log: $log_file)..."
    
    # ddrescue options:
    # -d: open input in direct mode
    # -D: --direct=on/off for both input and output
    # -r: number of retries
    # -R: reset on error
    # -b: block size
    if ddrescue --verbose --force -D --block-size=4096 -r 3 -R "$source" "$output" "$log_file"; then
        print_success "Acquisition d'image terminée"
        return 0
    else
        print_error "L'acquisition d'image a échoué"
        return 1
    fi
}

# Function: Calculate hashes
calculate_hashes() {
    local filepath=$1
    
    print_info "Calcul des empreintes cryptographiques..."
    
    local md5_hash=$(md5sum "$filepath" | awk '{print $1}')
    local sha256_hash=$(sha256sum "$filepath" | awk '{print $1}')
    
    print_success "MD5:    $md5_hash"
    print_success "SHA256: $sha256_hash"
    
    # Save to hash file
    local hash_file="${filepath}.hashes"
    cat > "$hash_file" << EOF
Verification Hashes for: $(basename "$filepath")
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

MD5:    $md5_hash
SHA256: $sha256_hash
EOF
    
    print_success "Empreintes sauvegardées dans: $hash_file"
    
    # Return as semicolon-separated values
    echo "$md5_hash;$sha256_hash"
}

# Function: Create evidence metadata
create_metadata() {
    local case_id=$1
    local evidence_id=$2
    local source=$3
    local output=$4
    local examiner=$5
    local device_info=$6
    local hashes=$7
    
    print_info "Création des métadonnées d'épreuve..."
    
    IFS='|' read -r model serial size <<< "$device_info"
    IFS=';' read -r md5_hash sha256_hash <<< "$hashes"
    
    local metadata_file="${output}.metadata"
    
    cat > "$metadata_file" << EOF
================================================================================
DFEPR - Evidence Metadata
================================================================================

CASE INFORMATION:
  Case ID:     $case_id
  Evidence ID: $evidence_id
  Date:        $(date -u +"%Y-%m-%d")
  Time:        $(date -u +"%H:%M:%S UTC")

EXAMINER:
  Name:        $examiner
  Signature:   ________________
  Date:        ________________

SOURCE DEVICE:
  Device:      $source
  Model:       $model
  Serial:      $serial
  Capacity:    $size bytes ($(numfmt --to=iec-i --suffix=B $size 2>/dev/null))

IMAGE INFORMATION:
  Filename:    $(basename "$output")
  Path:        $output
  File Size:   $(stat --format=%s "$output" 2>/dev/null) bytes
  Created:     $(date -u -r "$output" +"%Y-%m-%d %H:%M:%S UTC")

HASH VERIFICATION:
  Algorithm 1: MD5
  Hash:        $md5_hash
  
  Algorithm 2: SHA-256
  Hash:        $sha256_hash

ACQUISITION TOOL:
  Tool:        ddrescue
  Version:     $(ddrescue --version 2>/dev/null | head -n 1)
  Parameters:  -D --block-size=4096 -r 3 -R

CHAIN OF CUSTODY:

  ACQUISITION:
    Date/Time:    $(date -u +"%Y-%m-%d %H:%M:%S UTC")
    Examiner:     $examiner
    Signature:    ________________

================================================================================
EOF
    
    print_success "Métadonnées créées: $metadata_file"
}

# Function: Log activity
log_activity() {
    local case_id=$1
    local message=$2
    
    local log_file="$LOG_DIR/$case_id.log"
    mkdir -p "$LOG_DIR"
    
    echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $message" >> "$log_file"
}

# Function: Display usage
usage() {
    cat << EOF
Usage: $0 <source_device> <output_path> [case_id] [examiner]

Arguments:
  source_device   Device to acquire (e.g., /dev/sda)
  output_path     Output image file path
  case_id         Case identifier (optional, default: AUTO_<timestamp>)
  examiner        Examiner name (optional, default: Unknown)

Examples:
  $0 /dev/sda /evidence/images/disk1.img CASE_001 "John Doe"
  $0 /dev/sdb ./acquired_image.img

Requirements:
  - ddrescue
  - md5sum, sha256sum
  - blockdev
  - Root privileges or sudo access to device

EOF
}

# Main execution
main() {
    local source_device=${1:-}
    local output_path=${2:-}
    local case_id=${3:-"AUTO_$TIMESTAMP"}
    local examiner=${4:-"Unknown"}
    
    # Validate arguments
    if [ -z "$source_device" ] || [ -z "$output_path" ]; then
        print_error "Arguments manquants"
        usage
        exit 1
    fi
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        print_error "Ce script doit être exécuté en tant que root ou avec sudo"
        exit 1
    fi
    
    print_info "====== DFEPR - Image Acquisition ======"
    print_info "Case ID: $case_id"
    print_info "Examiner: $examiner"
    print_info "Timestamp: $TIMESTAMP"
    
    # Run steps
    check_prerequisites || exit 1
    validate_device "$source_device" || exit 1
    
    device_info=$(get_device_info "$source_device")
    
    acquire_image "$source_device" "$output_path" "$case_id" || exit 1
    
    hashes=$(calculate_hashes "$output_path")
    
    # Generate evidence ID
    evidence_id="${case_id}_$(basename "$output_path" .img)"
    
    create_metadata "$case_id" "$evidence_id" "$source_device" "$output_path" "$examiner" "$device_info" "$hashes"
    
    log_activity "$case_id" "Image Acquisition: Device=$source_device Output=$output_path MD5=$(echo $hashes | cut -d';' -f1)"
    
    print_success "====== Acquisition Terminée ======"
    print_info "Image: $output_path"
    print_info "Métadonnées: ${output_path}.metadata"
    print_info "Hashes: ${output_path}.hashes"
    
    exit 0
}

# Run main function with all arguments
main "$@"
