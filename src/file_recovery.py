#!/usr/bin/env python3
"""
DFEPR - File Recovery Module
Recovers deleted and hidden files from forensic evidence
"""

import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import tempfile


@dataclass
class RecoveredFile:
    """Information about a recovered file"""
    original_path: str  # Original location in filesystem
    filename: str
    size: int
    type: str  # File type (e.g., JPEG, PDF, etc.)
    recovery_method: str  # Method used to recover
    confidence: float  # Confidence level (0-1)
    recovered_path: str  # Path where recovered
    timestamp: str
    notes: str = ""


class FileRecoveryManager:
    """Manages file recovery from forensic evidence"""
    
    def __init__(self, case_id: str, storage_dir: str = "evidence/recovered"):
        """
        Initialize file recovery manager
        
        Args:
            case_id: Case identifier
            storage_dir: Base directory for recovered files
        """
        self.case_id = case_id
        self.storage_dir = Path(storage_dir) / case_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.recovery_log_path = self.storage_dir / "recovery_log.json"
        self.recovered_files: List[RecoveredFile] = []
        
        if self.recovery_log_path.exists():
            self._load_recovery_log()
    
    def recover_with_sleuthkit(
        self,
        image_path: str,
        output_dir: str = None,
        inode_range: Tuple[int, int] = None
    ) -> List[RecoveredFile]:
        """
        Recover deleted files using The Sleuth Kit (TSK)
        
        Args:
            image_path: Path to forensic image
            output_dir: Directory to output recovered files
            inode_range: Optional inode range to recover
            
        Returns:
            List of recovered files
        """
        if output_dir is None:
            output_dir = self.storage_dir / "tsk_recovery"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get filesystem info
            print(f"Analyzing filesystem: {image_path}")
            fsstat_output = subprocess.check_output(
                ["fsstat", image_path],
                text=True,
                stderr=subprocess.PIPE
            )
            
            # Extract inode range if not provided
            if inode_range is None:
                lines = fsstat_output.split('\n')
                for line in lines:
                    if 'Inode' in line and 'Range' in line:
                        # Parse "Range: 1 - 1234567"
                        parts = line.split('-')
                        if len(parts) >= 2:
                            end = int(parts[1].strip().split()[0])
                            inode_range = (1, end)
                            break
            
            if not inode_range:
                inode_range = (1, 100000)  # Default range
            
            print(f"Scanning inodes {inode_range[0]}-{inode_range[1]}")
            
            # Use icat to recover files
            recovered = []
            for inode in range(inode_range[0], min(inode_range[0] + 1000, inode_range[1])):
                try:
                    result = subprocess.run(
                        ["istat", image_path, str(inode)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if "Allocated" in result.stdout or "Unallocated" in result.stdout:
                        # File information found
                        filename = f"recovered_inode_{inode}.bin"
                        output_path = output_dir / filename
                        
                        # Try to recover using icat
                        with open(output_path, 'wb') as f:
                            cat_result = subprocess.run(
                                ["icat", image_path, str(inode)],
                                capture_output=True,
                                timeout=5
                            )
                            f.write(cat_result.stdout)
                        
                        recovered_file = RecoveredFile(
                            original_path=f"Inode {inode}",
                            filename=filename,
                            size=os.path.getsize(output_path),
                            type="unknown",
                            recovery_method="sleuthkit_icat",
                            confidence=0.5,
                            recovered_path=str(output_path),
                            timestamp=datetime.utcnow().isoformat() + "Z"
                        )
                        recovered.append(recovered_file)
                        self.recovered_files.append(recovered_file)
                
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    continue
            
            self._save_recovery_log()
            return recovered
        
        except subprocess.CalledProcessError as e:
            print(f"Error running TSK: {e}")
            return []
    
    def recover_with_photorec(
        self,
        image_path: str,
        output_dir: str = None,
        file_types: List[str] = None
    ) -> List[RecoveredFile]:
        """
        Recover deleted files using PhotoRec
        
        Args:
            image_path: Path to forensic image
            output_dir: Directory to output recovered files
            file_types: List of file types to recover (e.g. ['jpg', 'pdf'])
            
        Returns:
            List of recovered files
        """
        if output_dir is None:
            output_dir = self.storage_dir / "photorec_recovery"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # PhotoRec command
            cmd = ["photorec", "/d", str(output_dir), "/cmd", image_path, "recover"]
            
            print(f"Running PhotoRec on {image_path}")
            print("Note: This may take a long time for large images...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                print(f"PhotoRec error: {result.stderr}")
                return []
            
            # Scan recovered files
            recovered = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    file_size = os.path.getsize(filepath)
                    file_type = self._identify_file_type(filepath)
                    
                    # Filter by file type if specified
                    if file_types and file_type.lower() not in [ft.lower() for ft in file_types]:
                        continue
                    
                    recovered_file = RecoveredFile(
                        original_path="Recovered from unallocated space",
                        filename=file,
                        size=file_size,
                        type=file_type,
                        recovery_method="photorec",
                        confidence=0.7,
                        recovered_path=filepath,
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
                    recovered.append(recovered_file)
                    self.recovered_files.append(recovered_file)
            
            self._save_recovery_log()
            return recovered
        
        except subprocess.TimeoutExpired:
            print("PhotoRec recovery timed out")
            return []
        except subprocess.CalledProcessError as e:
            print(f"Error running PhotoRec: {e}")
            return []
    
    def recover_with_scalpel(
        self,
        image_path: str,
        config_file: str = None,
        output_dir: str = None
    ) -> List[RecoveredFile]:
        """
        Recover deleted files using Scalpel
        
        Args:
            image_path: Path to forensic image
            config_file: Scalpel configuration file
            output_dir: Directory to output recovered files
            
        Returns:
            List of recovered files
        """
        if output_dir is None:
            output_dir = self.storage_dir / "scalpel_recovery"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build Scalpel command
            cmd = ["scalpel", "-o", str(output_dir), image_path]
            
            if config_file and os.path.exists(config_file):
                cmd.insert(1, "-c")
                cmd.insert(2, config_file)
            
            print(f"Running Scalpel on {image_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                print(f"Scalpel error: {result.stderr}")
                return []
            
            # Scan recovered files
            recovered = []
            audit_file = output_dir / "audit.txt"
            
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    for line in f:
                        if line.startswith("File:"):
                            # Parse audit line
                            parts = line.split("|")
                            if len(parts) >= 2:
                                filepath = parts[1].strip()
                                if os.path.exists(filepath):
                                    file_size = os.path.getsize(filepath)
                                    file_type = self._identify_file_type(filepath)
                                    
                                    recovered_file = RecoveredFile(
                                        original_path="Recovered from unallocated space",
                                        filename=os.path.basename(filepath),
                                        size=file_size,
                                        type=file_type,
                                        recovery_method="scalpel",
                                        confidence=0.8,
                                        recovered_path=filepath,
                                        timestamp=datetime.utcnow().isoformat() + "Z"
                                    )
                                    recovered.append(recovered_file)
                                    self.recovered_files.append(recovered_file)
            
            self._save_recovery_log()
            return recovered
        
        except subprocess.TimeoutExpired:
            print("Scalpel recovery timed out")
            return []
        except subprocess.CalledProcessError as e:
            print(f"Error running Scalpel: {e}")
            return []
    
    @staticmethod
    def _identify_file_type(filepath: str) -> str:
        """
        Identify file type using 'file' command
        
        Args:
            filepath: Path to file
            
        Returns:
            File type description
        """
        try:
            result = subprocess.run(
                ["file", filepath],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Extract file type from "filename: type, ..."
            parts = result.stdout.split(":")
            if len(parts) >= 2:
                file_info = parts[1].strip()
                return file_info.split(",")[0]
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def _load_recovery_log(self) -> None:
        """Load recovery log from file"""
        try:
            with open(self.recovery_log_path, 'r') as f:
                data = json.load(f)
                self.recovered_files = [
                    RecoveredFile(**item) for item in data.get("recovered", [])
                ]
        except json.JSONDecodeError:
            self.recovered_files = []
    
    def _save_recovery_log(self) -> None:
        """Save recovery log to file"""
        data = {
            "case_id": self.case_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_recovered": len(self.recovered_files),
            "recovered": [asdict(f) for f in self.recovered_files]
        }
        
        with open(self.recovery_log_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_recovery_report(self) -> str:
        """Generate file recovery report"""
        report = f"""
================================================================================
FILE RECOVERY REPORT
================================================================================

Case ID: {self.case_id}
Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
Total Recovered Files: {len(self.recovered_files)}

================================================================================
RECOVERED FILES
================================================================================

"""
        
        if not self.recovered_files:
            report += "No files recovered.\n"
            return report
        
        # Group by recovery method
        by_method = {}
        for file in self.recovered_files:
            method = file.recovery_method
            if method not in by_method:
                by_method[method] = []
            by_method[method].append(file)
        
        for method, files in by_method.items():
            report += f"\nRecovery Method: {method.upper()}\n"
            report += f"Files Recovered: {len(files)}\n"
            report += "-" * 80 + "\n"
            
            for i, file in enumerate(files, 1):
                report += f"""
  [{i}] {file.filename}
      Size: {file.size} bytes
      Type: {file.type}
      Confidence: {file.confidence * 100:.1f}%
      Path: {file.recovered_path}
      Notes: {file.notes if file.notes else 'N/A'}
"""
        
        report += "\n" + "="*80 + "\n"
        return report
    
    def export_file_list(self, output_file: str) -> bool:
        """
        Export recovered files list as CSV
        
        Args:
            output_file: Path to output CSV file
            
        Returns:
            True if successful
        """
        try:
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'filename', 'size', 'type', 'recovery_method',
                    'confidence', 'recovered_path', 'timestamp'
                ])
                writer.writeheader()
                
                for file in self.recovered_files:
                    writer.writerow({
                        'filename': file.filename,
                        'size': file.size,
                        'type': file.type,
                        'recovery_method': file.recovery_method,
                        'confidence': f"{file.confidence * 100:.1f}%",
                        'recovered_path': file.recovered_path,
                        'timestamp': file.timestamp
                    })
            
            return True
        except Exception as e:
            print(f"Error exporting file list: {e}")
            return False


# Example usage
if __name__ == "__main__":
    recovery = FileRecoveryManager("CASE_2026_001")
    
    # Example: Recover with PhotoRec
    # recovered = recovery.recover_with_photorec("/path/to/image.img")
    
    # Example: Recover with Scalpel
    # recovered = recovery.recover_with_scalpel("/path/to/image.img")
    
    print(recovery.generate_recovery_report())
