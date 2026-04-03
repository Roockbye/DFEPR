#!/usr/bin/env python3
"""
DFEPR - Utility Functions
Common utilities for the forensic laboratory
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging


class Logger:
    """Centralized logging for DFEPR"""
    
    _logger = None
    
    @classmethod
    def setup(cls, case_id: str, log_dir: str = "evidence/cases") -> logging.Logger:
        """Setup centralized logger"""
        log_path = Path(log_dir) / f"{case_id}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        cls._logger = logging.getLogger(case_id)
        return cls._logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get logger instance"""
        if cls._logger is None:
            cls._logger = logging.getLogger("dfepr")
        return cls._logger


class SystemHelper:
    """System-level helper functions"""
    
    @staticmethod
    def run_command(
        command: str,
        timeout: int = 300,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        Run system command safely
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                timeout=timeout,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    @staticmethod
    def check_tool_available(tool_name: str) -> bool:
        """Check if tool is available"""
        return_code, _, _ = SystemHelper.run_command(f"which {tool_name}")
        return return_code == 0
    
    @staticmethod
    def get_disk_space(path: str) -> Dict[str, int]:
        """Get disk space information"""
        try:
            result = os.statvfs(path)
            total = result.f_blocks * result.f_frsize
            free = result.f_bavail * result.f_frsize
            used = total - free
            
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent_used": (used / total) * 100 if total > 0 else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def format_bytes(n_bytes: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if n_bytes < 1024.0:
                return f"{n_bytes:.2f} {unit}"
            n_bytes /= 1024.0
        return f"{n_bytes:.2f} PB"


class FileHelper:
    """File operation helpers"""
    
    @staticmethod
    def create_directory_structure(base_path: str, case_id: str) -> Dict[str, Path]:
        """Create standard directory structure"""
        paths = {
            "case": Path(base_path) / "evidence" / "cases" / case_id,
            "images": Path(base_path) / "evidence" / "images" / case_id,
            "recovered": Path(base_path) / "evidence" / "recovered" / case_id,
            "reports": Path(base_path) / "evidence" / "reports" / case_id,
            "temp": Path(base_path) / "evidence" / "temp" / case_id,
        }
        
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        
        return paths
    
    @staticmethod
    def safe_delete(file_path: str, secure: bool = False) -> bool:
        """
        Safely delete file
        
        Args:
            file_path: Path to delete
            secure: Use secure deletion (overwrite before delete)
            
        Returns:
            True if successful
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False
            
            if secure:
                # Overwrite with random data before deletion
                size = path.stat().st_size
                with open(path, 'wb') as f:
                    f.write(os.urandom(size))
            
            path.unlink()
            return True
        except Exception as e:
            Logger.get_logger().error(f"Failed to delete {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """Get comprehensive file information"""
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                "path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
            }
        except Exception as e:
            return {"error": str(e)}


class ConfigHelper:
    """Configuration file helpers"""
    
    @staticmethod
    def load_json_config(config_path: str) -> Dict:
        """Load JSON configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            Logger.get_logger().error(f"Failed to load config: {e}")
            return {}
    
    @staticmethod
    def save_json_config(config: Dict, config_path: str) -> bool:
        """Save JSON configuration"""
        try:
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            Logger.get_logger().error(f"Failed to save config: {e}")
            return False


class ValidationHelper:
    """Validation helpers for forensic data"""
    
    @staticmethod
    def validate_case_id(case_id: str) -> bool:
        """Validate case ID format"""
        # Format: TYPE_YEAR_NUMBER (e.g., THEFT_2026_000001)
        parts = case_id.split('_')
        if len(parts) < 3:
            return False
        
        # Check year is 4 digits
        try:
            year = int(parts[1])
            if year < 2000 or year > 2100:
                return False
        except ValueError:
            return False
        
        # Check number is numeric
        try:
            int(parts[2])
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def validate_evidence_id(evidence_id: str) -> bool:
        """Validate evidence ID format"""
        # Format: TYPE_YEAR_NUMBER_SEQUENCE
        parts = evidence_id.split('_')
        if len(parts) < 4:
            return False
        
        try:
            # Last part should be sequence number
            int(parts[-1])
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def validate_hash(hash_value: str, algorithm: str = "sha256") -> bool:
        """Validate hash format"""
        hash_lengths = {
            "md5": 32,
            "sha1": 40,
            "sha256": 64,
            "sha512": 128
        }
        
        expected_len = hash_lengths.get(algorithm.lower())
        if not expected_len:
            return False
        
        # Hash should be hexadecimal string
        if len(hash_value) != expected_len:
            return False
        
        try:
            int(hash_value, 16)
            return True
        except ValueError:
            return False


class TimestampHelper:
    """Timestamp and time-related helpers"""
    
    @staticmethod
    def get_utc_timestamp() -> str:
        """Get current UTC timestamp"""
        return datetime.utcnow().isoformat() + "Z"
    
    @staticmethod
    def format_timestamp(timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
        """Format ISO timestamp to readable format"""
        try:
            # Remove Z suffix if present
            ts = timestamp.rstrip('Z')
            dt = datetime.fromisoformat(ts)
            return dt.strftime(format_str)
        except Exception:
            return timestamp
    
    @staticmethod
    def get_readable_timestamp() -> str:
        """Get readable timestamp"""
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = Logger.setup("TEST_CASE")
    
    # Check tools
    if SystemHelper.check_tool_available("ddrescue"):
        print("✓ ddrescue available")
    else:
        print("✗ ddrescue not available")
    
    # Get disk space
    space_info = SystemHelper.get_disk_space(".")
    print(f"Free disk space: {SystemHelper.format_bytes(space_info.get('free', 0))}")
    
    # Validate case ID
    if ValidationHelper.validate_case_id("THEFT_2026_000001"):
        print("✓ Case ID valid")
    
    # Get timestamp
    print(f"UTC Timestamp: {TimestampHelper.get_utc_timestamp()}")
