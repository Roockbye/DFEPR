#!/usr/bin/env python3
"""
DFEPR - Database Management Module

Persistent storage for cases, evidence, and chain of custody records
using SQLite for portability and simplicity.

Author: DFEPR Development Team
License: GPL 3.0+
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.logging_handler import get_logger

logger = get_logger(__name__)


class EvidenceStatus(Enum):
    """Evidence status tracking."""
    CREATED = "created"
    ACQUIRED = "acquired"
    ANALYZED = "analyzed"
    RECOVERED = "recovered"
    REPORTED = "reported"
    ARCHIVED = "archived"
    DESTROYED = "destroyed"


@dataclass
class CaseRecord:
    """Case database record."""
    case_id: str
    description: str
    created_by: str
    created_date: str
    status: str = "active"
    archive_date: Optional[str] = None
    notes: str = ""


@dataclass
class EvidenceRecord:
    """Evidence database record."""
    evidence_id: str
    case_id: str
    description: str
    source: str
    date_acquired: str
    hash_sha256: str = ""
    hash_md5: str = ""
    status: str = "created"
    file_path: str = ""
    size_bytes: int = 0


class DatabaseManager:
    """
    Manages DFEPR database with SQLite.
    
    Provides persistent storage for:
    - Case information
    - Evidence metadata
    - Chain of custody records
    - Analysis results
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database (default: ~/.dfepr/dfepr.db)
        """
        if db_path is None:
            db_dir = Path.home() / '.dfepr'
            db_dir.mkdir(exist_ok=True, parents=True)
            db_path = db_dir / 'dfepr.db'
        
        self.db_path = Path(db_path)
        self.connection = None
        
        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # Create tables
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                archive_date TEXT,
                notes TEXT,
                updated_date TEXT
            );
            
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                date_acquired TEXT NOT NULL,
                hash_sha256 TEXT,
                hash_md5 TEXT,
                status TEXT DEFAULT 'created',
                file_path TEXT,
                size_bytes INTEGER DEFAULT 0,
                updated_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            );
            
            CREATE TABLE IF NOT EXISTS chain_of_custody (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT NOT NULL,
                action TEXT NOT NULL,
                person_name TEXT NOT NULL,
                person_title TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                items_affected TEXT,
                signature TEXT,
                notes TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
            );
            
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                result_summary TEXT NOT NULL,
                files_recovered INTEGER DEFAULT 0,
                anomalies_found INTEGER DEFAULT 0,
                analysis_date TEXT NOT NULL,
                analyst_name TEXT,
                FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_case_id ON evidence(case_id);
            CREATE INDEX IF NOT EXISTS idx_evidence_id ON chain_of_custody(evidence_id);
            CREATE INDEX IF NOT EXISTS idx_evidence_action ON chain_of_custody(action);
            """)
            
            self.connection.commit()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def create_case(self, case_id: str, description: str, 
                   created_by: str, notes: str = "") -> bool:
        """
        Create a new case.
        
        Args:
            case_id: Unique case identifier
            description: Case description
            created_by: User creating the case
            notes: Optional notes
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            INSERT INTO cases (case_id, description, created_by, created_date, notes, updated_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (case_id, description, created_by, now, notes, now))
            
            self.connection.commit()
            logger.info(f"Case created: {case_id}", case_id=case_id)
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Case already exists: {case_id}", case_id=case_id)
            return False
        except Exception as e:
            logger.error(f"Error creating case: {e}", case_id=case_id)
            return False

    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get case information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving case: {e}")
            return None

    def list_cases(self, status: str = None) -> List[Dict]:
        """
        List cases, optionally filtered by status.
        
        Args:
            status: Filter by status (active, archived)
            
        Returns:
            List of case dictionaries
        """
        try:
            cursor = self.connection.cursor()
            
            if status:
                cursor.execute("SELECT * FROM cases WHERE status = ? ORDER BY created_date DESC",
                             (status,))
            else:
                cursor.execute("SELECT * FROM cases ORDER BY created_date DESC")
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            return []

    def register_evidence(self, evidence_id: str, case_id: str, 
                         description: str, source: str) -> bool:
        """Register evidence for a case."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            # Verify case exists
            cursor.execute("SELECT case_id FROM cases WHERE case_id = ?", (case_id,))
            if not cursor.fetchone():
                logger.warning(f"Case not found: {case_id}")
                return False
            
            cursor.execute("""
            INSERT INTO evidence 
            (evidence_id, case_id, description, source, date_acquired, updated_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (evidence_id, case_id, description, source, now, now))
            
            self.connection.commit()
            logger.info(f"Evidence registered: {evidence_id}", 
                       case_id=case_id, evidence_id=evidence_id)
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Evidence already exists: {evidence_id}")
            return False
        except Exception as e:
            logger.error(f"Error registering evidence: {e}")
            return False

    def get_evidence(self, evidence_id: str) -> Optional[Dict]:
        """Get evidence information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving evidence: {e}")
            return None

    def list_evidence(self, case_id: str = None) -> List[Dict]:
        """List evidence, optionally filtered by case."""
        try:
            cursor = self.connection.cursor()
            
            if case_id:
                cursor.execute(
                    "SELECT * FROM evidence WHERE case_id = ? ORDER BY date_acquired DESC",
                    (case_id,)
                )
            else:
                cursor.execute("SELECT * FROM evidence ORDER BY date_acquired DESC")
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing evidence: {e}")
            return []

    def update_evidence_hash(self, evidence_id: str, sha256: str, md5: str = "") -> bool:
        """Update evidence hash values."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            UPDATE evidence 
            SET hash_sha256 = ?, hash_md5 = ?, updated_date = ?
            WHERE evidence_id = ?
            """, (sha256, md5, now, evidence_id))
            
            self.connection.commit()
            logger.info(f"Evidence hash updated: {evidence_id}", 
                       evidence_id=evidence_id)
            return True
        except Exception as e:
            logger.error(f"Error updating evidence hash: {e}")
            return False

    def update_evidence_status(self, evidence_id: str, status: str) -> bool:
        """Update evidence status."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            UPDATE evidence 
            SET status = ?, updated_date = ?
            WHERE evidence_id = ?
            """, (status, now, evidence_id))
            
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating evidence status: {e}")
            return False

    def add_custody_entry(self, evidence_id: str, action: str,
                         person_name: str, person_title: str,
                         location: str, description: str,
                         items_affected: str = "", signature: str = "",
                         notes: str = "") -> bool:
        """Add chain of custody entry."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            INSERT INTO chain_of_custody
            (evidence_id, action, person_name, person_title, location, 
             description, items_affected, signature, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (evidence_id, action, person_name, person_title, location,
                  description, items_affected, signature, notes, now))
            
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding custody entry: {e}")
            return False

    def get_custody_chain(self, evidence_id: str) -> List[Dict]:
        """Get complete chain of custody for evidence."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
            SELECT * FROM chain_of_custody 
            WHERE evidence_id = ? 
            ORDER BY timestamp ASC
            """, (evidence_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving custody chain: {e}")
            return []

    def record_analysis(self, evidence_id: str, analysis_type: str,
                       result_summary: str, files_recovered: int = 0,
                       anomalies_found: int = 0, analyst_name: str = "") -> bool:
        """Record analysis results."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            INSERT INTO analysis_results
            (evidence_id, analysis_type, result_summary, files_recovered, 
             anomalies_found, analysis_date, analyst_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (evidence_id, analysis_type, result_summary, files_recovered,
                  anomalies_found, now, analyst_name))
            
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording analysis: {e}")
            return False

    def get_analysis_results(self, evidence_id: str) -> List[Dict]:
        """Get analysis results for evidence."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
            SELECT * FROM analysis_results 
            WHERE evidence_id = ? 
            ORDER BY analysis_date DESC
            """, (evidence_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return []

    def archive_case(self, case_id: str) -> bool:
        """Archive a case."""
        try:
            cursor = self.connection.cursor()
            now = datetime.now(tz=None).isoformat()
            
            cursor.execute("""
            UPDATE cases 
            SET status = 'archived', archive_date = ?, updated_date = ?
            WHERE case_id = ?
            """, (now, now, case_id))
            
            self.connection.commit()
            logger.info(f"Case archived: {case_id}", case_id=case_id)
            return True
        except Exception as e:
            logger.error(f"Error archiving case: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM cases")
            total_cases = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM cases WHERE status = 'active'")
            active_cases = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM evidence")
            total_evidence = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM chain_of_custody")
            total_custody_entries = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM analysis_results")
            total_analyses = cursor.fetchone()['count']
            
            return {
                'total_cases': total_cases,
                'active_cases': active_cases,
                'total_evidence': total_evidence,
                'total_custody_entries': total_custody_entries,
                'total_analyses': total_analyses
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Module-level instance
_default_db: Optional[DatabaseManager] = None


def get_database_manager(db_path: Optional[Path] = None) -> DatabaseManager:
    """Get or create default database manager."""
    global _default_db
    if _default_db is None:
        _default_db = DatabaseManager(db_path)
    return _default_db


if __name__ == '__main__':
    # Example usage
    db = DatabaseManager()
    
    # Create case
    db.create_case('CASE-2024-001', 'Test investigation', 'Admin')
    
    # Register evidence
    db.register_evidence('EV-001', 'CASE-2024-001', 'Suspect disk', '/dev/sda')
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Database Statistics: {stats}")
    
    db.close()
