# DFEPR - Digital Forensics Lab Makefile
# Automates common laboratory tasks

.PHONY: help install setup clean test lint tests run-tests docs changelog logs

PYTHON := python3
PIP := pip3
SHELL := /bin/bash

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# Default target
help:
	@echo "$(BLUE)DFEPR - Digital Forensics Evidence Preservation & Recovery Lab$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo "  $(YELLOW)install$(NC)       - Install Python dependencies"
	@echo "  $(YELLOW)setup$(NC)         - Complete laboratory setup"
	@echo "  $(YELLOW)test$(NC)          - Run test suite"
	@echo "  $(YELLOW)lint$(NC)          - Run code linting"
	@echo "  $(YELLOW)clean$(NC)         - Clean temporary files"
	@echo "  $(YELLOW)docs$(NC)          - Generate documentation"
	@echo "  $(YELLOW)format$(NC)        - Format code with black"
	@echo "  $(YELLOW)check-tools$(NC)   - Check if forensic tools are installed"
	@echo "  $(YELLOW)logs$(NC)          - View recent logs"
	@echo ""
	@echo "$(GREEN)Example usage:$(NC)"
	@echo "  $(BLUE)make install$(NC)"
	@echo "  $(BLUE)make test$(NC)"
	@echo "  $(BLUE)make setup$(NC)"

# Install Python dependencies
install:
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# Complete setup
setup: install
	@echo "$(YELLOW)Setting up laboratory environment...$(NC)"
	chmod +x scripts/*.sh
	chmod +x src/*.py
	mkdir -p evidence/cases
	mkdir -p evidence/images
	mkdir -p evidence/recovered
	mkdir -p evidence/reports
	mkdir -p docs/procedures
	@echo "$(GREEN)✓ Laboratory setup complete$(NC)"

# Run tests
test:
	@echo "$(YELLOW)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v --tb=short
	@echo "$(GREEN)✓ Tests complete$(NC)"

run-tests:
	@echo "$(YELLOW)Running DFEPR tests...$(NC)"
	$(PYTHON) tests/test_dfepr.py
	@echo "$(GREEN)✓ Tests complete$(NC)"

# Code linting
lint:
	@echo "$(YELLOW)Running linting...$(NC)"
	$(PYTHON) -m flake8 src/ scripts/ tests/ --max-line-length=100
	@echo "$(GREEN)✓ Linting complete$(NC)"

# Code formatting
format:
	@echo "$(YELLOW)Formatting code with black...$(NC)"
	$(PYTHON) -m black src/ tests/ scripts/ --line-length=100
	@echo "$(GREEN)✓ Code formatted$(NC)"

# Clean temporary files
clean:
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Check forensic tools
check-tools:
	@echo "$(YELLOW)Checking forensic tools...$(NC)"
	@echo ""
	@if command -v ddrescue &> /dev/null; then \
		echo "$(GREEN)✓ ddrescue$(NC)"; \
	else \
		echo "$(RED)✗ ddrescue$(NC)"; \
	fi
	@if command -v sleuthkit &> /dev/null; then \
		echo "$(GREEN)✓ sleuthkit$(NC)"; \
	else \
		echo "$(RED)✗ sleuthkit$(NC)"; \
	fi
	@if command -v photorec &> /dev/null; then \
		echo "$(GREEN)✓ photorec$(NC)"; \
	else \
		echo "$(RED)✗ photorec$(NC)"; \
	fi
	@if command -v scalpel &> /dev/null; then \
		echo "$(GREEN)✓ scalpel$(NC)"; \
	else \
		echo "$(RED)✗ scalpel$(NC)"; \
	fi
	@if command -v md5sum &> /dev/null; then \
		echo "$(GREEN)✓ md5sum$(NC)"; \
	else \
		echo "$(RED)✗ md5sum$(NC)"; \
	fi
	@if command -v sha256sum &> /dev/null; then \
		echo "$(GREEN)✓ sha256sum$(NC)"; \
	else \
		echo "$(RED)✗ sha256sum$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Install missing tools with: sudo ./setup.sh$(NC)"

# View recent logs
logs:
	@echo "$(YELLOW)Recent logs:$(NC)"
	@find evidence/cases -name "*.log" -type f -mtime -1 2>/dev/null | \
		while read f; do \
			echo ""; \
			echo "$(GREEN)$$f:$(NC)"; \
			tail -10 "$$f"; \
		done || echo "$(YELLOW)No recent logs found$(NC)"

# Generate documentation
docs:
	@echo "$(YELLOW)Generating documentation...$(NC)"
	@echo "$(BLUE)Documentation files:$(NC)"
	@ls -lh docs/*.md
	@find docs/procedures -name "*.md" -type f | \
		while read f; do \
			echo "  - $$f"; \
		done
	@echo "$(GREEN)✓ Documentation available$(NC)"

# Show git status
status:
	@git status

# Show changelog
changelog:
	@echo "$(YELLOW)DFEPR Changelog:$(NC)"
	@echo ""
	@cat CHANGELOG.md | head -50

# Show project statistics
stats:
	@echo "$(BLUE)Project Statistics:$(NC)"
	@echo ""
	@echo "$(YELLOW)Python files:$(NC)"
	@find src/ tests/ -name "*.py" -type f | wc -l | xargs echo "  Count:"
	@find src/ tests/ -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print "  Lines: " $$1}'
	@echo ""
	@echo "$(YELLOW)Documentation:$(NC)"
	@find docs/ -name "*.md" -type f | wc -l | xargs echo "  Files:"
	@find docs/ -name "*.md" -type f -exec wc -l {} + | tail -1 | awk '{print "  Lines: " $$1}'
	@echo ""
	@echo "$(YELLOW)Scripts:$(NC)"
	@find scripts/ -name "*.sh" -type f | wc -l | xargs echo "  Count:"
	@echo ""
	@echo "$(YELLOW)Tests:$(NC)"
	@find tests/ -name "test_*.py" -type f | wc -l | xargs echo "  Count:"

# Quick test suite run
quick-test:
	@echo "$(YELLOW)Running quick tests...$(NC)"
	$(PYTHON) -m unittest tests.test_dfepr.TestValidationHelper -v 2>/dev/null || \
		$(PYTHON) tests/test_dfepr.py TestValidationHelper
	@echo "$(GREEN)✓ Quick test complete$(NC)"

# Install all requirements
requirements:
	@echo "$(YELLOW)Updating requirements...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt --upgrade
	@echo "$(GREEN)✓ Requirements updated$(NC)"

# Run all checks
all: clean lint test
	@echo "$(GREEN)✓ All checks passed$(NC)"

# Show help for a specific target
help-%:
	@echo "$(BLUE)Help for target: $(patsubst help-%,%,$@)$(NC)"
	@echo ""
	@case $(patsubst help-%,%,$@) in \
		install) echo "Installs Python dependencies from requirements.txt" ;; \
		setup) echo "Performs complete laboratory setup including install" ;; \
		test) echo "Runs the complete test suite using pytest" ;; \
		lint) echo "Runs flake8 linting on Python code" ;; \
		clean) echo "Removes temporary files and caches" ;; \
		check-tools) echo "Verifies forensic tools are installed" ;; \
		logs) echo "Displays recent case logs" ;; \
		docs) echo "Lists available documentation" ;; \
		*) echo "Unknown target. Run 'make help' for available targets" ;; \
	esac

# Phony targets
.PHONY: help install setup test lint clean check-tools logs docs status changelog stats quick-test requirements all help-%

# Default shell options
.SHELLFLAGS := -ec
