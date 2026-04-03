#!/bin/bash

################################################################################
# DFEPR Setup Script
# Installs dependencies and prepares the laboratory environment
################################################################################

echo "================================================"
echo "DFEPR - Digital Forensics Lab Setup"
echo "================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Notice: Some components require root access${NC}"
    echo "Continuing with available installations..."
fi

echo -e "\n${YELLOW}Installing system dependencies...${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

# Install based on OS
case "$OS" in
    ubuntu|debian)
        apt-get update
        apt-get install -y \
            gddrescue \
            sleuthkit \
            photorec \
            scalpel \
            md5sum \
            sha256sum \
            xxd \
            hexdump \
            python3 \
            python3-pip
        ;;
    fedora|rhel|centos)
        yum install -y \
            ddrescue \
            sleuthkit \
            photorec \
            scalpel \
            coreutils \
            vim-common \
            python3 \
            python3-pip
        ;;
    arch)
        pacman -Sy --noconfirm \
            ddrescue \
            sleuthkit \
            photorec \
            scalpel \
            python3 \
            python3-pip
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        echo "Please install dependencies manually"
        ;;
esac

echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

echo -e "\n${YELLOW}Creating directory structure...${NC}"
mkdir -p evidence/cases
mkdir -p evidence/images
mkdir -p evidence/recovered
mkdir -p evidence/reports
mkdir -p docs/procedures
mkdir -p docs/case_examples

echo -e "\n${YELLOW}Setting permissions...${NC}"
chmod 755 scripts/*.sh
chmod 755 src/*.py

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Review docs/ACPO_Guidelines.md"
echo "2. Configure case information"
echo "3. Run: ./scripts/acquire_image.sh --help"
echo ""
