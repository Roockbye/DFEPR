#!/usr/bin/env python3
"""
DFEPR - File Recovery Operations Manager
Handles PhotoRec, Scalpel, and TSK integration for file recovery
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
import tempfile
import shutil

from src.chain_of_custody import ChainOfCustody, CustodyAction
from src.hash_verifier import HashVerifier
from src.utilities import ValidationHelper, TimestampHelper
from src.logging_handler import StructuredLogger


class RecoveryTool(Enum):
    """Available recovery tools"""
    PHOTOREC = "photorec"
    SCALPEL = "scalpel"
    TSK_RECOVER = "tsk_recover"
    AUTOPSY = "autopsy"


class RecoveryStatus(Enum):
    """Recovery operation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class RecoveryTask:
    """Represents a file recovery task"""
    recovery_id: str
    case_id: str
    evidence_id: str
    evidence_path: str
    tool: RecoveryTool
    output_directory: str
    status: RecoveryStatus
    created_timestamp: str
    started_timestamp: Optional[str] = None
    completed_timestamp: Optional[str] = None
    total_files_found: int = 0
    recovered_files: int = 0
    recovered_size_bytes: int = 0
    error_message: Optional[str] = None
    pid: Optional[int] = None
    config: Dict = field(default_factory=dict)


class PhotoRecManager:
    """Manages PhotoRec recovery operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize PhotoRec manager"""
        self.logger = logger or StructuredLogger("recovery.photorec")
    
    def is_available(self) -> bool:
        """Check if PhotoRec is available"""
        return shutil.which("photorec") is not None
    
    def recover(self, source: str, output_dir: str, file_types: Optional[List[str]] = None) -> Dict:
        """
        Run PhotoRec recovery
        
        Args:
            source: Source device/file
            output_dir: Output directory for recovered files
            file_types: List of file types to recover (None = all)
        
        Returns:
            Recovery result dictionary
        """
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Build PhotoRec command
            cmd = ["photorec", "/d", output_dir, "/cmd", source]
            
            if file_types:
                # PhotoRec uses extension config file
                config_path = self._create_photorec_config(file_types)
                cmd.extend(["/rec", config_path])
            
            self.logger.info(f"Starting PhotoRec recovery: {source}")
            
            # Run PhotoRec in non-interactive mode
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                # Count recovered files
                recovered_count = self._count_recovered_files(output_dir)
                recovered_size = self._calculate_directory_size(output_dir)
                
                self.logger.info(f"PhotoRec completed: {recovered_count} files, {recovered_size} bytes")
                
                return {
                    "success": True,
                    "tool": "photorec",
                    "files_found": recovered_count,
                    "size_bytes": recovered_size,
                    "output_dir": output_dir,
                    "errors": []
                }
            else:
                self.logger.error(f"PhotoRec failed: {result.stderr}")
                return {
                    "success": False,
                    "tool": "photorec",
                    "error": result.stderr,
                    "errors": [result.stderr]
                }
        
        except subprocess.TimeoutExpired:
            self.logger.error("PhotoRec operation timed out")
            return {
                "success": False,
                "tool": "photorec",
                "error": "Operation timed out",
                "errors": ["Timeout after 1 hour"]
            }
        except Exception as e:
            self.logger.error(f"PhotoRec error: {e}")
            return {
                "success": False,
                "tool": "photorec",
                "error": str(e),
                "errors": [str(e)]
            }
    
    def _create_photorec_config(self, file_types: List[str]) -> str:
        """Create PhotoRec configuration file"""
        config_content = "# PhotoRec file type config\n"
        
        # PhotoRec extension mappings
        ext_map = {
            "jpg": "jpeg",
            "png": "png",
            "pdf": "pdf",
            "doc": "doc",
            "xls": "xls",
            "zip": "zip",
            "rar": "rar",
            "exe": "exe"
        }
        
        for ftype in file_types:
            if ftype in ext_map:
                config_content += f"search {ext_map[ftype]}\n"
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as f:
            f.write(config_content)
            return f.name
    
    def _count_recovered_files(self, directory: str) -> int:
        """Count recovered files in directory"""
        count = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                count += 1
        return count
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory contents"""
        total = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total


class ScalpelManager:
    """Manages Scalpel recovery operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize Scalpel manager"""
        self.logger = logger or StructuredLogger("recovery.scalpel")
    
    def is_available(self) -> bool:
        """Check if Scalpel is available"""
        return shutil.which("scalpel") is not None
    
    def recover(self, source_file: str, output_dir: str, config_file: Optional[str] = None) -> Dict:
        """
        Run Scalpel recovery
        
        Args:
            source_file: Source file to scan
            output_dir: Output directory for recovered files
            config_file: Scalpel configuration file (uses default if None)
        
        Returns:
            Recovery result dictionary
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Build Scalpel command
            cmd = ["scalpel", "-o", output_dir, source_file]
            
            if config_file and Path(config_file).exists():
                cmd.insert(1, "-c")
                cmd.insert(2, config_file)
            
            self.logger.info(f"Starting Scalpel recovery: {source_file}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                recovered_count = self._count_recovered_files(output_dir)
                recovered_size = self._calculate_directory_size(output_dir)
                
                self.logger.info(f"Scalpel completed: {recovered_count} files, {recovered_size} bytes")
                
                return {
                    "success": True,
                    "tool": "scalpel",
                    "files_found": recovered_count,
                    "size_bytes": recovered_size,
                    "output_dir": output_dir,
                    "errors": []
                }
            else:
                self.logger.error(f"Scalpel failed: {result.stderr}")
                return {
                    "success": False,
                    "tool": "scalpel",
                    "error": result.stderr,
                    "errors": [result.stderr]
                }
        
        except subprocess.TimeoutExpired:
            self.logger.error("Scalpel operation timed out")
            return {
                "success": False,
                "tool": "scalpel",
                "error": "Operation timed out",
                "errors": ["Timeout after 1 hour"]
            }
        except Exception as e:
            self.logger.error(f"Scalpel error: {e}")
            return {
                "success": False,
                "tool": "scalpel",
                "error": str(e),
                "errors": [str(e)]
            }
    
    def _count_recovered_files(self, directory: str) -> int:
        """Count recovered files"""
        count = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                count += 1
        return count
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total


class TSKRecoveryManager:
    """Manages The Sleuth Kit recovery operations"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize TSK manager"""
        self.logger = logger or StructuredLogger("recovery.tsk")
    
    def is_available(self) -> bool:
        """Check if TSK tools are available"""
        return shutil.which("tsk_recover") is not None or shutil.which("fls") is not None
    
    def recover(self, source: str, output_dir: str) -> Dict:
        """
        Run TSK recovery
        
        Args:
            source: Source device/file
            output_dir: Output directory
        
        Returns:
            Recovery result dictionary
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Use tsk_recover if available, otherwise use fls + icat
            if shutil.which("tsk_recover"):
                cmd = ["tsk_recover", "-e", source, output_dir]
            else:
                # Fallback: use fls to list files and icat to carve them
                self.logger.info("Using fls/icat for recovery")
                return self._recover_with_fls_icat(source, output_dir)
            
            self.logger.info(f"Starting TSK recovery: {source}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                recovered_count = self._count_recovered_files(output_dir)
                recovered_size = self._calculate_directory_size(output_dir)
                
                self.logger.info(f"TSK recovery completed: {recovered_count} files, {recovered_size} bytes")
                
                return {
                    "success": True,
                    "tool": "tsk_recover",
                    "files_found": recovered_count,
                    "size_bytes": recovered_size,
                    "output_dir": output_dir,
                    "errors": []
                }
            else:
                self.logger.error(f"TSK recovery failed: {result.stderr}")
                return {
                    "success": False,
                    "tool": "tsk_recover",
                    "error": result.stderr,
                    "errors": [result.stderr]
                }
        
        except subprocess.TimeoutExpired:
            self.logger.error("TSK operation timed out")
            return {
                "success": False,
                "tool": "tsk_recover",
                "error": "Operation timed out",
                "errors": ["Timeout after 1 hour"]
            }
        except Exception as e:
            self.logger.error(f"TSK error: {e}")
            return {
                "success": False,
                "tool": "tsk_recover",
                "error": str(e),
                "errors": [str(e)]
            }
    
    def _recover_with_fls_icat(self, source: str, output_dir: str) -> Dict:
        """Recover using fls and icat tools"""
        try:
            recovered_count = 0
            
            # List files using fls
            result = subprocess.run(
                ["fls", "-r", source],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                
                for file_entry in files:
                    if file_entry:
                        # Extract inode number (first field)
                        inode = file_entry.split()[0]
                        
                        # Use icat to extract file
                        output_file = Path(output_dir) / f"recovered_{recovered_count}.bin"
                        
                        with open(output_file, 'wb') as out:
                            result = subprocess.run(
                                ["icat", source, inode],
                                stdout=out,
                                stderr=subprocess.PIPE,
                                timeout=300
                            )
                            
                            if result.returncode == 0:
                                recovered_count += 1
            
            recovered_size = self._calculate_directory_size(output_dir)
            
            return {
                "success": True,
                "tool": "fls_icat",
                "files_found": recovered_count,
                "size_bytes": recovered_size,
                "output_dir": output_dir,
                "errors": []
            }
        
        except Exception as e:
            self.logger.error(f"fls/icat recovery error: {e}")
            return {
                "success": False,
                "tool": "fls_icat",
                "error": str(e),
                "errors": [str(e)]
            }
    
    def _count_recovered_files(self, directory: str) -> int:
        """Count recovered files"""
        count = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                count += 1
        return count
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size"""
        total = 0
        for item in Path(directory).rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total


class RecoveryManager:
    """
    Central manager for file recovery operations
    Orchestrates PhotoRec, Scalpel, and TSK integrations
    """
    
    def __init__(self, case_id: str, evidence_id: str, logger: Optional[StructuredLogger] = None):
        """Initialize recovery manager"""
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.logger = logger or StructuredLogger("recovery")
        
        # Initialize tool managers
        self.photorec = PhotoRecManager(self.logger)
        self.scalpel = ScalpelManager(self.logger)
        self.tsk = TSKRecoveryManager(self.logger)
        
        # Recovery tasks directory
        self.recovery_dir = Path.home() / ".dfepr" / "recoveries"
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
    
    def start_recovery(self, evidence_path: str, tool: RecoveryTool, 
                      output_dir: Optional[str] = None, config: Optional[Dict] = None) -> Dict:
        """
        Start a recovery operation
        
        Args:
            evidence_path: Path to evidence file/device
            tool: Recovery tool to use
            output_dir: Custom output directory (uses default if None)
            config: Tool-specific configuration
        
        Returns:
            Recovery task details
        """
        try:
            # Validate evidence path
            if not Path(evidence_path).exists():
                return {"success": False, "error": f"Evidence path not found: {evidence_path}"}
            
            # Generate recovery ID
            recovery_id = f"REC_{self.case_id}_{self.evidence_id}_{TimestampHelper.get_utc_iso()}"
            
            # Create output directory
            if not output_dir:
                output_dir = str(self.recovery_dir / recovery_id)
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Starting {tool.value} recovery: {recovery_id}")
            
            # Run recovery based on tool
            if tool == RecoveryTool.PHOTOREC:
                result = self.photorec.recover(evidence_path, output_dir, config)
            elif tool == RecoveryTool.SCALPEL:
                result = self.scalpel.recover(evidence_path, output_dir, config.get('config_file') if config else None)
            elif tool == RecoveryTool.TSK_RECOVER:
                result = self.tsk.recover(evidence_path, output_dir)
            else:
                return {"success": False, "error": f"Unsupported tool: {tool.value}"}
            
            if result.get("success"):
                # Record in chain of custody
                self._record_recovery_in_coc(recovery_id, tool, result)
                
                return {
                    "success": True,
                    "recovery_id": recovery_id,
                    "tool": tool.value,
                    "files_recovered": result.get("files_found", 0),
                    "size_bytes": result.get("size_bytes", 0),
                    "output_dir": output_dir,
                    "timestamp": TimestampHelper.get_utc_timestamp()
                }
            else:
                self.logger.error(f"Recovery failed: {result.get('error')}")
                return {
                    "success": False,
                    "recovery_id": recovery_id,
                    "error": result.get("error"),
                    "timestamp": TimestampHelper.get_utc_timestamp()
                }
        
        except Exception as e:
            self.logger.error(f"Recovery manager error: {e}")
            return {"success": False, "error": str(e)}
    
    def list_available_tools(self) -> Dict[str, bool]:
        """List available recovery tools"""
        return {
            "photorec": self.photorec.is_available(),
            "scalpel": self.scalpel.is_available(),
            "tsk_recover": self.tsk.is_available()
        }
    
    def _record_recovery_in_coc(self, recovery_id: str, tool: RecoveryTool, result: Dict):
        """Record recovery operation in chain of custody"""
        try:
            coc = ChainOfCustody(self.case_id, self.evidence_id)
            
            description = f"File recovery using {tool.value}: {result.get('files_found', 0)} files recovered ({result.get('size_bytes', 0)} bytes)"
            
            coc.add_entry(
                action=CustodyAction.RECOVERY,
                person_name="SYSTEM",
                person_title="Automated Recovery",
                location="Lab",
                description=description,
                items_affected=[recovery_id],
                notes=f"Tool output: {result.get('output_dir')}"
            )
            
            self.logger.info(f"Recovery recorded in CoC: {recovery_id}")
        
        except Exception as e:
            self.logger.warning(f"Failed to record recovery in CoC: {e}")


def get_recovery_manager(case_id: str, evidence_id: str) -> RecoveryManager:
    """Factory function for RecoveryManager"""
    return RecoveryManager(case_id, evidence_id)
