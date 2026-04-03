#!/usr/bin/env python3
"""
DFEPR - Report Generation and Export Module
Comprehensive reporting and data export functionality for forensic investigations
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
import csv

from src.database import get_database_manager
from src.statistics import get_statistics_collector
from src.utilities import TimestampHelper, SystemHelper
from src.logging_handler import StructuredLogger


class ReportFormat(Enum):
    """Supported report formats"""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML = "html"


class ReportType(Enum):
    """Types of reports"""
    CASE_SUMMARY = "case_summary"
    EVIDENCE_INVENTORY = "evidence_inventory"
    CHAIN_OF_CUSTODY = "chain_of_custody"
    ANALYSIS_REPORT = "analysis_report"
    STATISTICS = "statistics"
    EVIDENCE_SUMMARY = "evidence_summary"
    INVESTIGATION = "investigation"


@dataclass
class ReportMetadata:
    """Metadata for generated reports"""
    report_type: str
    report_format: str
    created_timestamp: str
    case_id: Optional[str] = None
    evidence_id: Optional[str] = None
    analyst: str = "DFEPR System"
    organization: str = "DFEPR"


class ReportGenerator:
    """
    Generate forensic investigation reports in multiple formats
    with ACPO compliance and professional formatting
    """
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize report generator"""
        self.logger = logger or StructuredLogger("reports")
        self.db = get_database_manager()
        self.stats = get_statistics_collector()
        self.reports_dir = Path.home() / ".dfepr" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_case_summary_report(self, case_id: str, 
                                    format: ReportFormat = ReportFormat.JSON) -> Dict[str, Any]:
        """
        Generate comprehensive case summary report
        
        Args:
            case_id: Case identifier
            format: Output format
            
        Returns:
            Report data dictionary
        """
        try:
            self.logger.info(f"Generating case summary for {case_id}")
            
            # Get case information
            case = self.db.get_case(case_id)
            if not case:
                return {"success": False, "error": f"Case not found: {case_id}"}
            
            # Get evidence list
            evidence_list = self.db.list_evidence(case_id)
            
            # Get statistics
            case_stats = self.stats.get_case_statistics(case_id)
            
            # Build report
            report_data = {
                "metadata": {
                    "report_type": ReportType.CASE_SUMMARY.value,
                    "report_format": format.value,
                    "created": TimestampHelper.get_utc_timestamp(),
                    "case_id": case_id
                },
                "case": {
                    "id": case.get('case_id'),
                    "status": case.get('status'),
                    "created": case.get('created_date'),
                    "modified": case.get('updated_date')
                },
                "statistics": {
                    "total_evidence": case_stats.total_evidence,
                    "custody_entries": case_stats.custody_entries,
                    "recovered_files_total": case_stats.recovered_files_total,
                    "analyses": case_stats.analysis_results,
                    "status": case_stats.status
                },
                "evidence": [
                    {
                        "id": e[1],
                        "description": e[2],
                        "source": e[3],
                        "acquired": e[4]
                    } for e in evidence_list
                ]
            }
            
            self.logger.info(f"Case summary report generated: {len(evidence_list)} evidence items")
            return {"success": True, "data": report_data, "format": format.value}
        
        except Exception as e:
            self.logger.error(f"Case summary report generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_evidence_inventory_report(self, case_id: str,
                                          format: ReportFormat = ReportFormat.JSON) -> Dict[str, Any]:
        """
        Generate detailed evidence inventory report
        
        Args:
            case_id: Case identifier
            format: Output format
            
        Returns:
            Report data dictionary
        """
        try:
            self.logger.info(f"Generating evidence inventory for {case_id}")
            
            evidence_list = self.db.list_evidence(case_id)
            
            inventory = []
            for evidence in evidence_list:
                evidence_id = evidence[1]
                
                # Get custody chain
                custody_chain = self.db.get_custody_chain(evidence_id)
                
                # Get analysis
                analyses = self.db.get_analysis_results(evidence_id)
                
                inventory.append({
                    "evidence_id": evidence_id,
                    "description": evidence[2],
                    "source": evidence[3],
                    "acquired": evidence[4],
                    "custody_entries": len(custody_chain),
                    "analyses": len(analyses),
                    "status": evidence[0] if evidence[0] else "unknown"
                })
            
            report_data = {
                "metadata": {
                    "report_type": ReportType.EVIDENCE_INVENTORY.value,
                    "report_format": format.value,
                    "created": TimestampHelper.get_utc_timestamp(),
                    "case_id": case_id
                },
                "summary": {
                    "total_items": len(inventory),
                    "total_custody_entries": sum(i['custody_entries'] for i in inventory),
                    "total_analyses": sum(i['analysis_results'] for i in inventory)
                },
                "inventory": inventory
            }
            
            self.logger.info(f"Evidence inventory report generated: {len(inventory)} items")
            return {"success": True, "data": report_data, "format": format.value}
        
        except Exception as e:
            self.logger.error(f"Evidence inventory report failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_chain_of_custody_report(self, evidence_id: str,
                                        format: ReportFormat = ReportFormat.JSON) -> Dict[str, Any]:
        """
        Generate chain of custody report for evidence
        
        Args:
            evidence_id: Evidence identifier
            format: Output format
            
        Returns:
            Report data dictionary
        """
        try:
            self.logger.info(f"Generating CoC report for {evidence_id}")
            
            custody_chain = self.db.get_custody_chain(evidence_id)
            
            coc_entries = []
            for entry in custody_chain:
                coc_entries.append({
                    "timestamp": entry[1],
                    "action": entry[2],
                    "person_name": entry[3],
                    "person_title": entry[4],
                    "location": entry[5],
                    "description": entry[6],
                    "items_affected": entry[7],
                    "signature": entry[8] if len(entry) > 8 else None,
                    "notes": entry[9] if len(entry) > 9 else None
                })
            
            report_data = {
                "metadata": {
                    "report_type": ReportType.CHAIN_OF_CUSTODY.value,
                    "report_format": format.value,
                    "created": TimestampHelper.get_utc_timestamp(),
                    "evidence_id": evidence_id
                },
                "statistics": {
                    "total_entries": len(coc_entries),
                    "time_span": self._calculate_timespan(coc_entries)
                },
                "chain_of_custody": coc_entries
            }
            
            self.logger.info(f"CoC report generated: {len(coc_entries)} entries")
            return {"success": True, "data": report_data, "format": format.value}
        
        except Exception as e:
            self.logger.error(f"CoC report failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_analysis_report(self, evidence_id: str,
                                format: ReportFormat = ReportFormat.JSON) -> Dict[str, Any]:
        """
        Generate analysis results report
        
        Args:
            evidence_id: Evidence identifier
            format: Output format
            
        Returns:
            Report data dictionary
        """
        try:
            self.logger.info(f"Generating analysis report for {evidence_id}")
            
            analyses = self.db.get_analysis_results(evidence_id)
            
            analysis_entries = []
            for analysis in analyses:
                analysis_entries.append({
                    "timestamp": analysis[1] if len(analysis) > 1 else None,
                    "analysis_type": analysis[2] if len(analysis) > 2 else None,
                    "analyst": analysis[3] if len(analysis) > 3 else None,
                    "data": json.loads(analysis[4]) if len(analysis) > 4 and analysis[4] else {}
                })
            
            report_data = {
                "metadata": {
                    "report_type": ReportType.ANALYSIS_REPORT.value,
                    "report_format": format.value,
                    "created": TimestampHelper.get_utc_timestamp(),
                    "evidence_id": evidence_id
                },
                "statistics": {
                    "total_analyses": len(analysis_entries),
                    "analysis_types": list(set(a.get('analysis_type') for a in analysis_entries if a.get('analysis_type')))
                },
                "analyses": analysis_entries
            }
            
            self.logger.info(f"Analysis report generated: {len(analysis_entries)} analyses")
            return {"success": True, "data": report_data, "format": format.value}
        
        except Exception as e:
            self.logger.error(f"Analysis report failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_statistics_report(self, case_id: Optional[str] = None,
                                  format: ReportFormat = ReportFormat.JSON) -> Dict[str, Any]:
        """
        Generate statistics and analytics report
        
        Args:
            case_id: Optional case identifier (if None, system-wide stats)
            format: Output format
            
        Returns:
            Report data dictionary
        """
        try:
            if case_id:
                self.logger.info(f"Generating statistics for case {case_id}")
                case_stats = self.stats.get_case_statistics(case_id)
                
                stats_data = {
                    "case_id": case_id,
                    "total_evidence": case_stats.total_evidence,
                    "custody_entries": case_stats.custody_entries,
                    "recovered_files_total": case_stats.recovered_files_total,
                    "status": case_stats.status
                }
            else:
                self.logger.info("Generating system-wide statistics")
                system_stats = self.stats.get_system_statistics()
                
                stats_data = {
                    "total_cases": system_stats.total_cases,
                    "active_cases": system_stats.active_cases,
                    "archived_cases": system_stats.archived_cases,
                    "total_evidence": system_stats.total_evidence,
                    "custody_entries": system_stats.custody_entries,
                    "analyses": system_stats.analyses,
                    "recovered_files_total": system_stats.recovered_files_total,
                    "database_size_mb": system_stats.database_size_mb
                }
            
            report_data = {
                "metadata": {
                    "report_type": ReportType.STATISTICS.value,
                    "report_format": format.value,
                    "created": TimestampHelper.get_utc_timestamp(),
                    "case_id": case_id
                },
                "statistics": stats_data
            }
            
            self.logger.info("Statistics report generated")
            return {"success": True, "data": report_data, "format": format.value}
        
        except Exception as e:
            self.logger.error(f"Statistics report failed: {e}")
            return {"success": False, "error": str(e)}
    
    def export_to_json(self, report_data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export report to JSON format"""
        try:
            if output_file:
                output_path = Path(output_file)
            else:
                timestamp = TimestampHelper.get_utc_timestamp()
                output_path = self.reports_dir / f"report_{timestamp}.json"
            
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.logger.info(f"Report exported to JSON: {output_path}")
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f"JSON export failed: {e}")
            return ""
    
    def export_to_csv(self, report_data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export report data to CSV format"""
        try:
            if output_file:
                output_path = Path(output_file)
            else:
                timestamp = TimestampHelper.get_utc_timestamp()
                output_path = self.reports_dir / f"report_{timestamp}.csv"
            
            # Extract data based on report type
            report_type = report_data.get('metadata', {}).get('report_type')
            data_key = None
            fieldnames = []
            
            if report_type == ReportType.EVIDENCE_INVENTORY.value:
                data_key = 'inventory'
                fieldnames = ['evidence_id', 'case_id', 'description', 'file_path', 'file_hash', 'hash_type']
            elif report_type == ReportType.CHAIN_OF_CUSTODY.value:
                data_key = 'chain_of_custody'
                fieldnames = ['evidence_id', 'action', 'timestamp', 'reason', 'analyst']
            elif report_type == ReportType.ANALYSIS_REPORT.value:
                data_key = 'analysis_results'
                fieldnames = ['analysis_id', 'evidence_id', 'analysis_type', 'findings', 'timestamp']
            
            if not data_key:
                self.logger.warning(f"CSV export not supported for {report_type}")
                return ""
            
            rows = report_data.get('data', {}).get(data_key, [])
            
            # Write CSV (even if empty)
            actual_fieldnames = rows[0].keys() if rows else fieldnames
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=actual_fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            self.logger.info(f"Report exported to CSV: {output_path}")
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")
            return ""
    
    def export_to_text(self, report_data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export report to human-readable text format"""
        try:
            if output_file:
                output_path = Path(output_file)
            else:
                timestamp = TimestampHelper.get_utc_timestamp()
                output_path = self.reports_dir / f"report_{timestamp}.txt"
            
            lines = []
            lines.append("=" * 80)
            lines.append("DFEPR FORENSIC INVESTIGATION REPORT")
            lines.append("=" * 80)
            
            # Add metadata
            metadata = report_data.get('metadata', {})
            lines.append(f"\nReport Type: {metadata.get('report_type', 'Unknown').replace('_', ' ').title()}")
            lines.append(f"Generated: {metadata.get('created', 'Unknown')}")
            if metadata.get('case_id'):
                lines.append(f"Case ID: {metadata.get('case_id')}")
            if metadata.get('evidence_id'):
                lines.append(f"Evidence ID: {metadata.get('evidence_id')}")
            
            lines.append("\n" + "-" * 80)
            
            # Add content based on report type
            report_type = metadata.get('report_type')
            data = report_data.get('data', {})
            
            if report_type == ReportType.CASE_SUMMARY.value:
                lines.extend(self._format_case_summary_text(data))
            elif report_type == ReportType.EVIDENCE_INVENTORY.value:
                lines.extend(self._format_evidence_inventory_text(data))
            elif report_type == ReportType.CHAIN_OF_CUSTODY.value:
                lines.extend(self._format_coc_text(data))
            elif report_type == ReportType.STATISTICS.value:
                lines.extend(self._format_statistics_text(data))
            
            lines.append("\n" + "=" * 80)
            lines.append(f"Report generated by DFEPR on {TimestampHelper.get_utc_timestamp()}")
            lines.append("=" * 80)
            
            with open(output_path, 'w') as f:
                f.write("\n".join(lines))
            
            self.logger.info(f"Report exported to TEXT: {output_path}")
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f"TEXT export failed: {e}")
            return ""
    
    def _format_case_summary_text(self, data: Dict) -> List[str]:
        """Format case summary as text"""
        lines = []
        lines.append("\nCASE INFORMATION:")
        case = data.get('case', {})
        lines.append(f"  Case ID: {case.get('id', 'Unknown')}")
        lines.append(f"  Status: {case.get('status', 'Unknown')}")
        lines.append(f"  Created: {case.get('created', 'Unknown')}")
        
        lines.append("\nSTATISTICS:")
        stats = data.get('statistics', {})
        lines.append(f"  Total Evidence: {stats.get('total_evidence', 0)}")
        lines.append(f"  Custody Entries: {stats.get('custody_entries', 0)}")
        lines.append(f"  Recovered Files: {stats.get('recovered_files_total', 0)}")
        
        lines.append("\nEVIDENCE ITEMS:")
        for evidence in data.get('evidence', []):
            lines.append(f"  - {evidence.get('id')}: {evidence.get('description')}")
            lines.append(f"    Source: {evidence.get('source')}")
            lines.append(f"    Acquired: {evidence.get('acquired')}")
        
        return lines
    
    def _format_evidence_inventory_text(self, data: Dict) -> List[str]:
        """Format evidence inventory as text"""
        lines = []
        summary = data.get('summary', {})
        lines.append(f"\nEVIDENCE INVENTORY SUMMARY:")
        lines.append(f"  Total Items: {summary.get('total_items', 0)}")
        lines.append(f"  Total Custody Entries: {summary.get('total_custody_entries', 0)}")
        lines.append(f"  Total Analyses: {summary.get('total_analyses', 0)}")
        
        lines.append("\nDETAILED INVENTORY:")
        for item in data.get('inventory', []):
            lines.append(f"  {item.get('evidence_id')}")
            lines.append(f"    Description: {item.get('description')}")
            lines.append(f"    Source: {item.get('source')}")
            lines.append(f"    Custody Entries: {item.get('custody_entries')}")
            lines.append(f"    Analyses: {item.get('analysis_results')}")
        
        return lines
    
    def _format_coc_text(self, data: Dict) -> List[str]:
        """Format chain of custody as text"""
        lines = []
        stats = data.get('statistics', {})
        lines.append(f"\nCHAIN OF CUSTODY:")
        lines.append(f"  Total Entries: {stats.get('total_entries', 0)}")
        
        lines.append("\nCUSTODY ENTRIES:")
        for entry in data.get('chain_of_custody', []):
            lines.append(f"  {entry.get('timestamp')}")
            lines.append(f"    Action: {entry.get('action')}")
            lines.append(f"    Person: {entry.get('person_name')} ({entry.get('person_title')})")
            lines.append(f"    Location: {entry.get('location')}")
            lines.append(f"    Description: {entry.get('description')}")
        
        return lines
    
    def _format_statistics_text(self, data: Dict) -> List[str]:
        """Format statistics as text"""
        lines = []
        lines.append("\nSTATISTICS:")
        stats = data.get('statistics', {})
        for key, value in stats.items():
            display_key = key.replace('_', ' ').title()
            lines.append(f"  {display_key}: {value}")
        return lines
    
    def _calculate_timespan(self, entries: List[Dict]) -> str:
        """Calculate time span between first and last entries"""
        if len(entries) < 2:
            return "N/A"
        
        first_time = entries[0].get('timestamp', '')
        last_time = entries[-1].get('timestamp', '')
        
        return f"{first_time} to {last_time}"


def get_report_generator() -> ReportGenerator:
    """Factory function for ReportGenerator"""
    return ReportGenerator()
