#!/usr/bin/env python3
"""
Project statistics and analytics module for DFEPR.

Provides comprehensive statistics, metrics, and analytics for
DFEPR investigations, cases, and system operations.

Author: DFEPR Development Team
License: GPL 3.0+
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import json

from src.logging_handler import get_logger
from src.database import DatabaseManager

logger = get_logger(__name__)


@dataclass
class CaseStatistics:
    """Statistics for a single case."""
    case_id: str
    total_evidence: int = 0
    custody_entries: int = 0
    analysis_results: int = 0
    recovered_files_total: int = 0
    status: str = "active"
    created_date: Optional[str] = None


@dataclass
class SystemStatistics:
    """Overall system statistics."""
    total_cases: int = 0
    active_cases: int = 0
    archived_cases: int = 0
    total_evidence: int = 0
    total_custody_entries: int = 0
    total_analyses: int = 0
    files_recovered_total: int = 0
    database_size_mb: float = 0


class StatisticsCollector:
    """
    Collects and analyzes statistics from DFEPR operations.
    
    Provides metrics for:
    - Case management
    - Evidence tracking
    - File recovery
    - Database usage
    - System performance
    """

    def __init__(self, database_path: Optional[Path] = None):
        """
        Initialize statistics collector.
        
        Args:
            database_path: Path to DFEPR database
        """
        self.db = DatabaseManager(database_path)

    def get_system_statistics(self) -> SystemStatistics:
        """Get overall system statistics."""
        try:
            db_stats = self.db.get_statistics()
            
            # Get database file size
            db_size_mb = 0
            if self.db.db_path.exists():
                db_size_mb = self.db.db_path.stat().st_size / (1024 * 1024)
            
            stats = SystemStatistics(
                total_cases=db_stats.get('total_cases', 0),
                total_evidence=db_stats.get('total_evidence', 0),
                total_custody_entries=db_stats.get('total_custody_entries', 0),
                total_analyses=db_stats.get('total_analyses', 0),
                database_size_mb=db_size_mb
            )
            
            return stats
        except Exception as e:
            logger.error(f"Error collecting system statistics: {e}")
            return SystemStatistics()

    def get_case_statistics(self, case_id: str) -> CaseStatistics:
        """Get statistics for specific case."""
        try:
            case = self.db.get_case(case_id)
            if not case:
                return CaseStatistics(case_id=case_id)
            
            evidence_list = self.db.list_evidence(case_id)
            
            # Count custody entries for all evidence
            custody_count = 0
            recovered_count = 0
            
            for evidence in evidence_list:
                chain = self.db.get_custody_chain(evidence['evidence_id'])
                custody_count += len(chain)
                
                results = self.db.get_analysis_results(evidence['evidence_id'])
                recovered_count += sum(r.get('files_recovered', 0) for r in results)
            
            stats = CaseStatistics(
                case_id=case_id,
                total_evidence=len(evidence_list),
                custody_entries=custody_count,
                recovered_files_total=recovered_count,
                status=case.get('status', 'active'),
                created_date=case.get('created_date')
            )
            
            return stats
        except Exception as e:
            logger.error(f"Error collecting case statistics: {e}")
            return CaseStatistics(case_id=case_id)

    def get_evidence_summary(self, case_id: str) -> List[Dict]:
        """Get summary of all evidence in a case."""
        try:
            evidence_list = self.db.list_evidence(case_id)
            
            summaries = []
            for evidence in evidence_list:
                custody_chain = self.db.get_custody_chain(evidence['evidence_id'])
                analyses = self.db.get_analysis_results(evidence['evidence_id'])
                
                summary = {
                    'evidence_id': evidence['evidence_id'],
                    'description': evidence['description'],
                    'status': evidence['status'],
                    'size_bytes': evidence['size_bytes'],
                    'date_acquired': evidence['date_acquired'],
                    'custody_entries': len(custody_chain),
                    'analyses': len(analyses),
                    'files_recovered': sum(a.get('files_recovered', 0) for a in analyses)
                }
                summaries.append(summary)
            
            return summaries
        except Exception as e:
            logger.error(f"Error getting evidence summary: {e}")
            return []

    def get_custody_timeline(self, evidence_id: str) -> List[Dict]:
        """Get chain of custody timeline for evidence."""
        try:
            chain = self.db.get_custody_chain(evidence_id)
            
            timeline = []
            for entry in chain:
                item = {
                    'timestamp': entry['timestamp'],
                    'action': entry['action'],
                    'person': f"{entry['person_name']} ({entry['person_title']})",
                    'location': entry['location'],
                    'description': entry['description']
                }
                timeline.append(item)
            
            return timeline
        except Exception as e:
            logger.error(f"Error getting custody timeline: {e}")
            return []

    def get_analysis_report(self, case_id: str) -> Dict:
        """Generate comprehensive analysis report for case."""
        try:
            case_stats = self.get_case_statistics(case_id)
            evidence_list = self.db.list_evidence(case_id)
            
            report = {
                'case_id': case_id,
                'generated_at': datetime.now(tz=None).isoformat(),
                'case_statistics': {
                    'total_evidence': case_stats.total_evidence,
                    'custody_entries': case_stats.custody_entries,
                    'recovered_files': case_stats.recovered_files_total,
                    'status': case_stats.status
                },
                'evidence': []
            }
            
            for evidence in evidence_list:
                analyses = self.db.get_analysis_results(evidence['evidence_id'])
                
                evidence_report = {
                    'evidence_id': evidence['evidence_id'],
                    'description': evidence['description'],
                    'source': evidence['source'],
                    'status': evidence['status'],
                    'analyses': [
                        {
                            'type': a['analysis_type'],
                            'summary': a['result_summary'],
                            'files_recovered': a['files_recovered'],
                            'anomalies': a['anomalies_found'],
                            'analyst': a['analyst_name']
                        }
                        for a in analyses
                    ]
                }
                report['evidence'].append(evidence_report)
            
            return report
        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return {}

    def export_statistics_json(self, case_id: str, output_file: Path) -> bool:
        """Export case statistics to JSON."""
        try:
            stats = self.get_case_statistics(case_id)
            report = self.get_analysis_report(case_id)
            
            data = {
                'statistics': {
                    'case_id': stats.case_id,
                    'total_evidence': stats.total_evidence,
                    'custody_entries': stats.custody_entries,
                    'recovered_files': stats.recovered_files_total,
                    'status': stats.status
                },
                'report': report
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Statistics exported to {output_file}", case_id=case_id)
            return True
        except Exception as e:
            logger.error(f"Error exporting statistics: {e}")
            return False

    def print_system_summary(self):
        """Print system statistics summary to console."""
        stats = self.get_system_statistics()
        
        print("\n" + "="*60)
        print("DFEPR System Statistics")
        print("="*60)
        print(f"Total Cases:              {stats.total_cases}")
        print(f"Total Evidence Items:     {stats.total_evidence}")
        print(f"Chain of Custody Entries: {stats.total_custody_entries}")
        print(f"Analysis Results:         {stats.total_analyses}")
        print(f"Database Size:            {stats.database_size_mb:.2f} MB")
        print("="*60 + "\n")

    def print_case_summary(self, case_id: str):
        """Print case statistics summary to console."""
        stats = self.get_case_statistics(case_id)
        
        print(f"\n{'='*60}")
        print(f"Case: {stats.case_id}")
        print(f"{'='*60}")
        print(f"Status:                 {stats.status}")
        print(f"Total Evidence:         {stats.total_evidence}")
        print(f"Custody Entries:        {stats.custody_entries}")
        print(f"Files Recovered:        {stats.recovered_files_total}")
        print(f"Created:                {stats.created_date}")
        print(f"{'='*60}\n")


# Module-level instance
_default_collector: Optional[StatisticsCollector] = None


def get_statistics_collector(database_path: Optional[Path] = None) -> StatisticsCollector:
    """Get or create default statistics collector."""
    global _default_collector
    if _default_collector is None:
        _default_collector = StatisticsCollector(database_path)
    return _default_collector


if __name__ == '__main__':
    # Example usage
    collector = StatisticsCollector()
    
    print("System Statistics:")
    collector.print_system_summary()
    
    # Create sample case for demo
    collector.db.create_case('DEMO_2026_000001', 'Demo case', 'Demo User')
    collector.db.register_evidence('EV-DEMO-0001', 'DEMO_2026_000001', 'Demo evidence', '/dev/sda')
    
    print("Case Statistics:")
    collector.print_case_summary('DEMO_2026_000001')
