#!/usr/bin/env python3
"""
Advanced validation for DFEPR operations.

Comprehensive validation rules for data integrity, ACPO compliance,
and forensic investigation standards.

Author: DFEPR Development Team
License: GPL 3.0+
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path

from src.logging_handler import get_logger

logger = get_logger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    level: ValidationLevel
    code: str
    message: str
    details: Dict = None


class DataValidator:
    """Advanced data validation for DFEPR operations."""

    # Case ID format: TYPE_YEAR_NUMBER (e.g., THEFT_2026_000001)
    CASE_ID_PATTERN = r'^[A-Z_]+_\d{4}_\d{6}$'
    
    # Evidence ID pattern: EV-XXXX-YYYY (e.g., EV-2026-0001)
    EVIDENCE_ID_PATTERN = r'^EV-\d{4}-\d{4}$'
    
    # Hash patterns
    MD5_PATTERN = r'^[a-f0-9]{32}$'
    SHA256_PATTERN = r'^[a-f0-9]{64}$'
    SHA512_PATTERN = r'^[a-f0-9]{128}$'

    def __init__(self):
        """Initialize validator."""
        self.results: List[ValidationResult] = []

    def validate_case_id(self, case_id: str) -> Tuple[bool, str]:
        """
        Validate case ID format.
        
        Args:
            case_id: Case identifier to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not case_id:
            return False, "Case ID cannot be empty"
        
        if not re.match(self.CASE_ID_PATTERN, case_id):
            return False, (
                f"Invalid case ID format: {case_id}\n"
                f"Expected format: TYPE_YEAR_NUMBER (e.g., THEFT_2026_000001)"
            )
        
        return True, ""

    def validate_evidence_id(self, evidence_id: str) -> Tuple[bool, str]:
        """Validate evidence ID format."""
        if not evidence_id:
            return False, "Evidence ID cannot be empty"
        
        if not re.match(self.EVIDENCE_ID_PATTERN, evidence_id):
            return False, (
                f"Invalid evidence ID format: {evidence_id}\n"
                f"Expected format: EV-YEAR-NUMBER (e.g., EV-2026-0001)"
            )
        
        return True, ""

    def validate_hash(self, hash_value: str, algorithm: str = None) -> Tuple[bool, str]:
        """
        Validate hash format.
        
        Args:
            hash_value: Hash string to validate
            algorithm: Hash algorithm (md5, sha256, sha512)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hash_value:
            return False, "Hash value cannot be empty"
        
        hash_lower = hash_value.lower()
        
        if algorithm:
            patterns = {
                'md5': self.MD5_PATTERN,
                'sha256': self.SHA256_PATTERN,
                'sha512': self.SHA512_PATTERN
            }
            pattern = patterns.get(algorithm.lower())
            
            if pattern and not re.match(pattern, hash_lower):
                return False, f"Invalid {algorithm} hash format: {hash_value}"
        else:
            # Try to detect algorithm from hash length
            if len(hash_lower) == 32 and re.match(self.MD5_PATTERN, hash_lower):
                return True, ""
            elif len(hash_lower) == 64 and re.match(self.SHA256_PATTERN, hash_lower):
                return True, ""
            elif len(hash_lower) == 128 and re.match(self.SHA512_PATTERN, hash_lower):
                return True, ""
            else:
                return False, f"Unknown hash format: {hash_value}"
        
        return True, ""

    def validate_file_exists(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate that file exists and is accessible.
        
        Args:
            filepath: Path to file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(filepath)
        
        if not path.exists():
            return False, f"File not found: {filepath}"
        
        if not path.is_file():
            return False, f"Path is not a file: {filepath}"
        
        try:
            with open(path, 'rb') as f:
                f.read(1)
        except PermissionError:
            return False, f"Permission denied: {filepath}"
        except Exception as e:
            return False, f"Cannot access file: {filepath} ({e})"
        
        return True, ""

    def validate_file_permissions(self, filepath: str, writable: bool = True) -> Tuple[bool, str]:
        """Validate file permissions."""
        path = Path(filepath)
        
        if writable and not path.parent.is_dir():
            return False, f"Parent directory does not exist: {path.parent}"
        
        if writable:
            try:
                # Try creating a test file
                test_file = path.parent / '.dfepr_test'
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                return False, f"Cannot write to directory: {path.parent} ({e})"
        
        return True, ""

    def validate_directory_structure(self, base_dir: str) -> List[ValidationResult]:
        """
        Validate DFEPR directory structure.
        
        Args:
            base_dir: Base directory path
            
        Returns:
            List of validation results
        """
        results = []
        base_path = Path(base_dir)
        
        required_dirs = ['cases', 'images', 'recovered', 'reports', 'metadata']
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            
            if not dir_path.exists():
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    code='MISSING_DIR',
                    message=f"Missing directory: {dir_path}",
                    details={'directory': str(dir_path)}
                ))
            elif not dir_path.is_dir():
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    code='NOT_DIRECTORY',
                    message=f"Path is not a directory: {dir_path}",
                    details={'path': str(dir_path)}
                ))
        
        return results

    def validate_evidence_integrity(self, evidence_path: str, 
                                   expected_hash: str = None,
                                   hash_algorithm: str = 'sha256') -> Tuple[bool, str]:
        """
        Validate evidence file integrity.
        
        Args:
            evidence_path: Path to evidence file
            expected_hash: Expected hash value
            hash_algorithm: Hash algorithm to use
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file exists
        is_valid, msg = self.validate_file_exists(evidence_path)
        if not is_valid:
            return False, msg
        
        # If no expected hash, just verify file is readable
        if not expected_hash:
            return True, ""
        
        # Calculate hash and compare
        import hashlib
        try:
            path = Path(evidence_path)
            hasher = hashlib.new(hash_algorithm)
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    hasher.update(chunk)
            
            calculated_hash = hasher.hexdigest()
            
            if calculated_hash.lower() != expected_hash.lower():
                return False, (
                    f"Hash mismatch for {evidence_path}\n"
                    f"Expected: {expected_hash}\n"
                    f"Calculated: {calculated_hash}"
                )
            
            return True, ""
        except Exception as e:
            return False, f"Error calculating hash: {e}"

    def validate_case_description(self, description: str, 
                                 min_length: int = 10,
                                 max_length: int = 500) -> Tuple[bool, str]:
        """
        Validate case description.
        
        Args:
            description: Case description text
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description:
            return False, "Case description cannot be empty"
        
        if len(description) < min_length:
            return False, f"Description too short (minimum {min_length} characters)"
        
        if len(description) > max_length:
            return False, f"Description too long (maximum {max_length} characters)"
        
        # Check for minimum meaningful content
        if description.count(' ') < 2:
            return False, "Description must contain meaningful sentences"
        
        return True, ""

    def validate_officer_name(self, name: str) -> Tuple[bool, str]:
        """Validate officer name."""
        if not name or len(name.strip()) == 0:
            return False, "Officer name cannot be empty"
        
        if len(name) < 3:
            return False, "Officer name too short"
        
        if len(name) > 100:
            return False, "Officer name too long"
        
        return True, ""

    def validate_agency_name(self, agency: str) -> Tuple[bool, str]:
        """Validate agency name."""
        if not agency or len(agency.strip()) == 0:
            return False, "Agency name cannot be empty"
        
        if len(agency) < 3:
            return False, "Agency name too short"
        
        if len(agency) > 200:
            return False, "Agency name too long"
        
        return True, ""

    def validate_acpo_compliance(self, case_data: Dict) -> List[ValidationResult]:
        """
        Validate ACPO compliance for case.
        
        Args:
            case_data: Case data dictionary
            
        Returns:
            List of validation results
        """
        results = []
        
        # Principle 1: No modification
        if 'case_id' in case_data and not case_data.get('write_block_enabled'):
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                code='ACPO_P1_WARNING',
                message="Write-blocking not confirmed for this case",
                details=case_data
            ))
        
        # Principle 2: Chain of custody
        if not case_data.get('officer_name'):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                code='ACPO_P2_ERROR',
                message="Officer name required for chain of custody",
                details=case_data
            ))
        
        # Principle 3: Documentation
        if not case_data.get('description') or len(case_data.get('description', '')) < 10:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                code='ACPO_P3_ERROR',
                message="Adequate case description required for documentation",
                details=case_data
            ))
        
        # Principle 4: Senior management
        if not case_data.get('agency_name'):
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                code='ACPO_P4_WARNING',
                message="Agency information recommended for senior management oversight",
                details=case_data
            ))
        
        return results

    def validate_all(self, case_data: Dict) -> Tuple[bool, List[ValidationResult]]:
        """
        Run comprehensive validation on case data.
        
        Args:
            case_data: Case data dictionary
            
        Returns:
            Tuple of (all_valid, list_of_results)
        """
        results = []
        
        # Validate case ID
        if 'case_id' in case_data:
            is_valid, msg = self.validate_case_id(case_data['case_id'])
            if not is_valid:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    code='INVALID_CASE_ID',
                    message=msg
                ))
        
        # Validate description
        if 'description' in case_data:
            is_valid, msg = self.validate_case_description(case_data['description'])
            if not is_valid:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    code='INVALID_DESCRIPTION',
                    message=msg
                ))
        
        # Validate officer
        if 'officer_name' in case_data:
            is_valid, msg = self.validate_officer_name(case_data['officer_name'])
            if not is_valid:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    code='INVALID_OFFICER',
                    message=msg
                ))
        
        # Validate agency
        if 'agency_name' in case_data:
            is_valid, msg = self.validate_agency_name(case_data['agency_name'])
            if not is_valid:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    code='INVALID_AGENCY',
                    message=msg
                ))
        
        # ACPO compliance
        results.extend(self.validate_acpo_compliance(case_data))
        
        # Check for errors
        has_errors = any(r.level == ValidationLevel.ERROR for r in results)
        
        return not has_errors, results


# Module-level instance
_default_validator: Optional[DataValidator] = None


def get_validator() -> DataValidator:
    """Get or create default validator instance."""
    global _default_validator
    if _default_validator is None:
        _default_validator = DataValidator()
    return _default_validator


if __name__ == '__main__':
    # Example usage
    validator = DataValidator()
    
    # Test case ID validation
    print("Case ID validation:")
    valid, msg = validator.validate_case_id('THEFT_2026_000001')
    print(f"  THEFT_2026_000001: {valid} {msg}")
    
    # Test evidence ID validation
    print("\nEvidence ID validation:")
    valid, msg = validator.validate_evidence_id('EV-2026-0001')
    print(f"  EV-2026-0001: {valid} {msg}")
    
    # Test hash validation
    print("\nHash validation:")
    valid, msg = validator.validate_hash('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'sha256')
    print(f"  Valid SHA256: {valid}")
    
    # Test comprehensive validation
    print("\nComprehensive validation:")
    case_data = {
        'case_id': 'THEFT_2026_000001',
        'description': 'This is a comprehensive test case for a data theft investigation.',
        'officer_name': 'John Analyst',
        'agency_name': 'Test Police Department'
    }
    all_valid, results = validator.validate_all(case_data)
    print(f"  All valid: {all_valid}")
    for result in results:
        print(f"    {result.level.value}: {result.message}")
