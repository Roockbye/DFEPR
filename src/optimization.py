#!/usr/bin/env python3
"""
DFEPR - Database Optimization Module

Performance enhancements including batch operations, indexing, and query optimization
for handling large-scale forensic investigations.

Features:
- Batch evidence registration for bulk imports
- Database indexing on frequently queried fields
- Query optimization utilities
- Performance profiling and statistics
- Connection pooling management

Author: DFEPR Development Team
License: GPL 3.0+
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.logging_handler import StructuredLogger
from src.database import get_database_manager


@dataclass
class PerformanceMetrics:
    """Metrics for optimization tracking"""
    operation: str
    duration_ms: float
    items_processed: int
    items_per_second: float
    timestamp: str


class DatabaseOptimizer:
    """Database optimization and performance enhancement utilities"""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize optimizer"""
        self.logger = logger or StructuredLogger("optimization")
        self.db = get_database_manager()
        self.metrics_history: List[PerformanceMetrics] = []
    
    def create_optimized_indexes(self) -> Dict[str, bool]:
        """
        Create indexes on frequently queried fields
        Returns dict with index creation status
        """
        indexes = {
            "idx_case_id": "CREATE INDEX IF NOT EXISTS idx_case_id ON evidence(case_id)",
            "idx_status": "CREATE INDEX IF NOT EXISTS idx_status ON evidence(status)",
            "idx_evidence_status": "CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(case_id, status)",
            "idx_hash_sha256": "CREATE INDEX IF NOT EXISTS idx_hash_sha256 ON evidence(hash_sha256)",
            "idx_hash_md5": "CREATE INDEX IF NOT EXISTS idx_hash_md5 ON evidence(hash_md5)",
            "idx_coc_evidence": "CREATE INDEX IF NOT EXISTS idx_coc_evidence ON chain_of_custody(evidence_id)",
            "idx_coc_timestamp": "CREATE INDEX IF NOT EXISTS idx_coc_timestamp ON chain_of_custody(timestamp)",
            "idx_analysis_evidence": "CREATE INDEX IF NOT EXISTS idx_analysis_evidence ON analysis_results(evidence_id)",
            "idx_case_status": "CREATE INDEX IF NOT EXISTS idx_case_status ON cases(case_id, status)",
            "idx_analysis_type": "CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type)"
        }
        
        results = {}
        cursor = self.db.connection.cursor()
        
        try:
            for index_name, sql in indexes.items():
                cursor.execute(sql)
                results[index_name] = True
                self.logger.info(f"Index created: {index_name}")
        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")
            results = {k: False for k in indexes.keys()}
        finally:
            self.db.connection.commit()
        
        return results
    
    def batch_register_evidence(self, evidence_items: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Register multiple evidence items in a single transaction
        
        Args:
            evidence_items: List of evidence dictionaries
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        start_time = time.time()
        successful = 0
        failed = 0
        
        cursor = self.db.connection.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            for item in evidence_items:
                try:
                    cursor.execute("""
                        INSERT INTO evidence 
                        (evidence_id, case_id, description, source, date_acquired, 
                         hash_sha256, hash_md5, status, file_path, size_bytes, updated_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['evidence_id'],
                        item['case_id'],
                        item.get('description', ''),
                        item.get('source', 'manual'),
                        item.get('date_acquired', datetime.utcnow().isoformat() + 'Z'),
                        item.get('hash_sha256', ''),
                        item.get('hash_md5', ''),
                        item.get('status', 'created'),
                        item.get('file_path', ''),
                        item.get('size_bytes', 0),
                        datetime.utcnow().isoformat() + 'Z'
                    ))
                    successful += 1
                except Exception as e:
                    self.logger.warning(f"Failed to register evidence {item.get('evidence_id')}: {e}")
                    failed += 1
            
            cursor.execute("COMMIT")
            
            duration_ms = (time.time() - start_time) * 1000
            items_per_second = (successful + failed) / (duration_ms / 1000) if duration_ms > 0 else 0
            
            metric = PerformanceMetrics(
                operation="batch_register_evidence",
                duration_ms=duration_ms,
                items_processed=successful + failed,
                items_per_second=items_per_second,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            self.metrics_history.append(metric)
            
            self.logger.info(f"Batch registration completed: {successful} successful, {failed} failed in {duration_ms:.2f}ms")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.logger.error(f"Batch registration failed: {e}")
        
        return successful, failed
    
    def batch_register_hashes(self, hash_items: List[Dict[str, str]]) -> Tuple[int, int]:
        """
        Update multiple evidence hashes in a batch operation
        
        Args:
            hash_items: List of dicts with evidence_id, sha256, md5
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        start_time = time.time()
        successful = 0
        failed = 0
        
        cursor = self.db.connection.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            for item in hash_items:
                try:
                    cursor.execute("""
                        UPDATE evidence 
                        SET hash_sha256 = ?, hash_md5 = ?, updated_date = ?
                        WHERE evidence_id = ?
                    """, (
                        item.get('sha256', ''),
                        item.get('md5', ''),
                        datetime.utcnow().isoformat() + 'Z',
                        item['evidence_id']
                    ))
                    successful += 1
                except Exception as e:
                    self.logger.warning(f"Failed to update hash for {item.get('evidence_id')}: {e}")
                    failed += 1
            
            cursor.execute("COMMIT")
            
            duration_ms = (time.time() - start_time) * 1000
            items_per_second = (successful + failed) / (duration_ms / 1000) if duration_ms > 0 else 0
            
            metric = PerformanceMetrics(
                operation="batch_register_hashes",
                duration_ms=duration_ms,
                items_processed=successful + failed,
                items_per_second=items_per_second,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            self.metrics_history.append(metric)
            
            self.logger.info(f"Batch hash update completed: {successful} successful in {duration_ms:.2f}ms")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.logger.error(f"Batch hash update failed: {e}")
        
        return successful, failed
    
    def batch_add_custody_entries(self, custody_items: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Add multiple chain of custody entries in a batch operation
        
        Args:
            custody_items: List of CoC entry dictionaries
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        start_time = time.time()
        successful = 0
        failed = 0
        
        cursor = self.db.connection.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            for item in custody_items:
                try:
                    cursor.execute("""
                        INSERT INTO chain_of_custody
                        (evidence_id, action, person_name, person_title, location,
                         description, items_affected, signature, notes, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['evidence_id'],
                        item['action'],
                        item.get('person_name', 'Unknown'),
                        item.get('person_title', 'Analyst'),
                        item.get('location', 'Lab'),
                        item.get('description', ''),
                        item.get('items_affected', '1'),
                        item.get('signature', ''),
                        item.get('notes', ''),
                        item.get('timestamp', datetime.utcnow().isoformat() + 'Z')
                    ))
                    successful += 1
                except Exception as e:
                    self.logger.warning(f"Failed to add CoC entry for {item.get('evidence_id')}: {e}")
                    failed += 1
            
            cursor.execute("COMMIT")
            
            duration_ms = (time.time() - start_time) * 1000
            items_per_second = (successful + failed) / (duration_ms / 1000) if duration_ms > 0 else 0
            
            metric = PerformanceMetrics(
                operation="batch_add_custody_entries",
                duration_ms=duration_ms,
                items_processed=successful + failed,
                items_per_second=items_per_second,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            self.metrics_history.append(metric)
            
            self.logger.info(f"Batch CoC entry completed: {successful} successful in {duration_ms:.2f}ms")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.logger.error(f"Batch CoC entry failed: {e}")
        
        return successful, failed
    
    def optimize_queries(self) -> Dict[str, Any]:
        """
        Optimize query performance
        Returns optimization statistics
        """
        cursor = self.db.connection.cursor()
        
        try:
            # Enable query optimizer
            cursor.execute("PRAGMA optimize")
            
            # Analyze query performance
            cursor.execute("PRAGMA query_only = OFF")
            
            # Get database statistics
            cursor.execute("SELECT COUNT(*) as total_cases FROM cases")
            case_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as total_evidence FROM evidence")
            evidence_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as total_coc FROM chain_of_custody")
            coc_count = cursor.fetchone()[0]
            
            stats = {
                "total_cases": case_count,
                "total_evidence": evidence_count,
                "total_coc_entries": coc_count,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info(f"Database optimization complete: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Query optimization failed: {e}")
            return {}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate performance report from metrics history
        """
        if not self.metrics_history:
            return {"total_operations": 0, "metrics": []}
        
        total_items = sum(m.items_processed for m in self.metrics_history)
        total_time_ms = sum(m.duration_ms for m in self.metrics_history)
        avg_items_per_sec = total_items / (total_time_ms / 1000) if total_time_ms > 0 else 0
        
        return {
            "total_operations": len(self.metrics_history),
            "total_items_processed": total_items,
            "total_time_ms": total_time_ms,
            "average_items_per_second": avg_items_per_sec,
            "metrics": [
                {
                    "operation": m.operation,
                    "duration_ms": m.duration_ms,
                    "items_processed": m.items_processed,
                    "items_per_second": m.items_per_second,
                    "timestamp": m.timestamp
                }
                for m in self.metrics_history
            ]
        }


_optimizer_instance: Optional[DatabaseOptimizer] = None


def get_optimizer() -> DatabaseOptimizer:
    """Factory function to get optimizer singleton"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = DatabaseOptimizer()
    return _optimizer_instance
