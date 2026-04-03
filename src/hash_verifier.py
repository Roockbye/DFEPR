#!/usr/bin/env python3
"""
DFEPR - Hash Verification Module
Verifies cryptographic integrity of forensic evidence
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime
import concurrent.futures
import time


class HashVerifier:
    """Verifies and manages cryptographic hashes of evidence"""
    
    CHUNK_SIZE = 65536  # 64KB chunks for memory efficiency
    ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]
    
    def __init__(self, case_id: str, storage_dir: str = "evidence/cases"):
        """
        Initialize hash verifier
        
        Args:
            case_id: Case identifier
            storage_dir: Base directory for storing records
        """
        self.case_id = case_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.storage_dir / f"{case_id}_hashes.json"
        self.verification_log = self.storage_dir / f"{case_id}_verification.log"
        
        self.hashes: Dict[str, Dict[str, str]] = {}
        if self.records_file.exists():
            self._load_records()
    
    def calculate_hash(
        self,
        filepath: str,
        algorithms: list = None,
        progress_callback=None
    ) -> Dict[str, str]:
        """
        Calculate cryptographic hashes for a file
        
        Args:
            filepath: Path to file
            algorithms: List of algorithms to use (default: ["md5", "sha256"])
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary of {algorithm: hash_value}
        """
        if algorithms is None:
            algorithms = ["md5", "sha256"]
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_size = os.path.getsize(filepath)
        hashers = {algo: hashlib.new(algo) for algo in algorithms}
        bytes_read = 0
        
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    for hasher in hashers.values():
                        hasher.update(chunk)
                    
                    bytes_read += len(chunk)
                    if progress_callback:
                        progress = (bytes_read / file_size) * 100
                        progress_callback(progress)
        
        except IOError as e:
            raise IOError(f"Error reading file: {e}")
        
        return {algo: hasher.hexdigest() for algo, hasher in hashers.items()}
    
    def verify_file_hash(
        self,
        filepath: str,
        expected_hash: str,
        algorithm: str = "sha256"
    ) -> Tuple[bool, str]:
        """
        Verify a file against an expected hash
        
        Args:
            filepath: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            Tuple of (is_valid, actual_hash)
        """
        hashes = self.calculate_hash(filepath, [algorithm])
        actual_hash = hashes[algorithm]
        
        is_valid = actual_hash.lower() == expected_hash.lower()
        
        # Log verification
        status = "PASS" if is_valid else "FAIL"
        self._log_verification(
            filepath, algorithm, expected_hash, actual_hash, status
        )
        
        return is_valid, actual_hash
    
    def register_hash(
        self,
        evidence_id: str,
        filepath: str,
        algorithms: list = None,
        description: str = ""
    ) -> Dict[str, str]:
        """
        Register hashes for evidence
        
        Args:
            evidence_id: Evidence identifier
            filepath: Path to evidence file
            algorithms: List of algorithms
            description: Description of evidence
            
        Returns:
            Dictionary of calculated hashes
        """
        if algorithms is None:
            algorithms = ["md5", "sha256"]
        
        print(f"Calculating hashes for {filepath}...")
        hashes = self.calculate_hash(filepath, algorithms)
        
        self.hashes[evidence_id] = {
            "filepath": filepath,
            "description": description,
            "hashes": hashes,
            "file_size": os.path.getsize(filepath),
            "registered_date": datetime.utcnow().isoformat() + "Z"
        }
        
        self._save_records()
        return hashes
    
    def verify_integrity(
        self,
        evidence_id: str,
        filepath: str = None
    ) -> Dict:
        """
        Verify integrity of evidence
        
        Args:
            evidence_id: Evidence identifier
            filepath: Optional filepath (uses registered path if not provided)
            
        Returns:
            Verification results dictionary
        """
        if evidence_id not in self.hashes:
            return {"status": "error", "message": "Evidence not registered"}
        
        record = self.hashes[evidence_id]
        check_path = filepath or record["filepath"]
        
        if not os.path.exists(check_path):
            return {"status": "error", "message": f"File not found: {check_path}"}
        
        results = {
            "evidence_id": evidence_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filepath": check_path,
            "verifications": {}
        }
        
        # Verify each hash
        for algo, expected_hash in record["hashes"].items():
            is_valid, actual_hash = self.verify_file_hash(
                check_path, expected_hash, algo
            )
            results["verifications"][algo] = {
                "expected": expected_hash,
                "actual": actual_hash,
                "status": "PASS" if is_valid else "FAIL"
            }
        
        # Overall status
        all_pass = all(
            v["status"] == "PASS" for v in results["verifications"].values()
        )
        results["overall_status"] = "PASS" if all_pass else "FAIL"
        
        return results
    
    def _load_records(self) -> None:
        """Load hash records from file"""
        try:
            with open(self.records_file, 'r') as f:
                data = json.load(f)
                self.hashes = data.get("hashes", {})
        except json.JSONDecodeError:
            self.hashes = {}
    
    def _save_records(self) -> None:
        """Save hash records to file"""
        data = {
            "case_id": self.case_id,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "hashes": self.hashes
        }
        
        with open(self.records_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _log_verification(
        self,
        filepath: str,
        algorithm: str,
        expected: str,
        actual: str,
        status: str
    ) -> None:
        """Log verification event"""
        log_entry = (
            f"[{datetime.utcnow().isoformat()}Z] "
            f"{status} | {algorithm.upper()} | {filepath} | "
            f"Expected: {expected[:16]}... | Actual: {actual[:16]}...\n"
        )
        
        with open(self.verification_log, 'a') as f:
            f.write(log_entry)
    
    def generate_report(self) -> str:
        """Generate hash verification report"""
        report = f"""
================================================================================
HASH VERIFICATION REPORT
================================================================================

Case ID: {self.case_id}
Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

================================================================================
REGISTERED EVIDENCE
================================================================================

"""
        
        if not self.hashes:
            report += "No evidence registered.\n"
            return report
        
        for evidence_id, record in self.hashes.items():
            report += f"""
Evidence ID: {evidence_id}
Description: {record.get("description", "N/A")}
File: {record.get("filepath", "N/A")}
Size: {record.get("file_size", "N/A")} bytes
Registered: {record.get("registered_date", "N/A")}

Hashes:
"""
            
            for algo, hash_value in record["hashes"].items():
                report += f"  {algo.upper():8} : {hash_value}\n"
            
            report += "\n"
        
        report += "="*80 + "\n"
        return report


class HashMatch:
    """Compare hashes between files"""
    
    @staticmethod
    def compare_files(file1: str, file2: str, algorithm: str = "sha256") -> bool:
        """
        Compare hashes of two files
        
        Args:
            file1: Path to first file
            file2: Path to second file
            algorithm: Hash algorithm to use
            
        Returns:
            True if hashes match
        """
        verifier = HashVerifier("temp")
        
        hash1 = verifier.calculate_hash(file1, [algorithm])[algorithm]
        hash2 = verifier.calculate_hash(file2, [algorithm])[algorithm]
        
        return hash1.lower() == hash2.lower()
    
    @staticmethod
    def generate_hash_list(directory: str, output_file: str = None) -> Dict[str, str]:
        """
        Generate hash list for all files in directory
        
        Args:
            directory: Directory to hash
            output_file: Optional file to save list
            
        Returns:
            Dictionary of {filepath: hash}
        """
        verifier = HashVerifier("directory_scan")
        hashes = {}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    file_hash = verifier.calculate_hash(
                        filepath, ["sha256"]
                    )["sha256"]
                    hashes[filepath] = file_hash
                    print(f"✓ {filepath}")
                except Exception as e:
                    print(f"✗ {filepath}: {e}")
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(hashes, f, indent=2)
        
        return hashes


# Example usage
if __name__ == "__main__":
    # Initialize verifier
    verifier = HashVerifier("CASE_2026_001")
    
    # Example: Register evidence
    # verifier.register_hash(
    #     "EVIDENCE_001",
    #     "/path/to/image.img",
    #     description="Suspect Hard Drive Image"
    # )
    
    # Verify integrity
    # results = verifier.verify_integrity("EVIDENCE_001")
    # print(json.dumps(results, indent=2))
    
    # Generate report
    print(verifier.generate_report())
