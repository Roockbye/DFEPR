#!/usr/bin/env python3
"""
DFEPR - Advanced Analytics Module

Sophisticated forensic data analysis including:
- Evidence correlation detection
- Timeline generation from file metadata
- Anomaly identification
- Statistical trend analysis
- Hash collision detection
- Temporal analysis
- Pattern recognition

Author: DFEPR Development Team
License: GPL 3.0+
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

from src.logging_handler import StructuredLogger
from src.database import get_database_manager


class AnomalyType(Enum):
    """Types of detected anomalies"""
    HASH_DUPLICATE = "hash_duplicate"
    TIMELINE_GAP = "timeline_gap"
    LARGE_FILE = "large_file"
    UNUSUAL_PATTERN = "unusual_pattern"
    INTEGRITY_CHANGE = "integrity_change"
    METADATA_INCONSISTENCY = "metadata_inconsistency"


class CorrelationType(Enum):
    """Types of evidence correlations"""
    HASH_MATCH = "hash_match"
    TEMPORAL_PROXIMITY = "temporal_proximity"
    SAME_SOURCE = "same_source"
    METADATA_SIMILARITY = "metadata_similarity"
    FILE_TYPE_CLUSTER = "file_type_cluster"


@dataclass
class AnalyticsMetric:
    """Single analytics metric data point"""
    metric_type: str
    metric_name: str
    metric_value: Any
    timestamp: str
    case_id: Optional[str] = None
    severity: str = "info"


@dataclass
class CorrelationLink:
    """Represents a correlation between two evidence items"""
    evidence_id_1: str
    evidence_id_2: str
    correlation_type: CorrelationType
    confidence: float
    details: Dict[str, Any]


@dataclass
class AnomalyAlert:
    """Alert for detected anomaly"""
    anomaly_type: AnomalyType
    anomaly_id: str
    description: str
    affected_items: List[str]
    severity: str
    timestamp: str
    context: Dict[str, Any]


class AdvancedAnalytics:
    """
    Advanced forensic analysis capabilities for DFEPR
    Provides correlations, timeline analysis, and anomaly detection
    """
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """Initialize analytics engine"""
        self.logger = logger or StructuredLogger("analytics")
        self.db = get_database_manager()
        self.metrics_history: List[AnalyticsMetric] = []
        self.anomalies: List[AnomalyAlert] = []
        self.correlations: List[CorrelationLink] = []
    
    def detect_hash_duplicates(self, case_id: str) -> List[CorrelationLink]:
        """
        Detect evidence items with duplicate hashes
        Indicates possible copied or linked files
        """
        duplicates = []
        
        try:
            cursor = self.db.connection.cursor()
            
            # Query for duplicate SHA256 hashes
            cursor.execute("""
                SELECT hash_sha256, COUNT(*) as count, GROUP_CONCAT(evidence_id, ',') as ids
                FROM evidence
                WHERE case_id = ? AND hash_sha256 != '' AND hash_sha256 IS NOT NULL
                GROUP BY hash_sha256
                HAVING count > 1
            """, (case_id,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                hash_val = row[0]
                count = row[1]
                ids = row[2].split(',')
                
                # Create correlation for each pair
                for i, id1 in enumerate(ids):
                    for id2 in ids[i+1:]:
                        correlation = CorrelationLink(
                            evidence_id_1=id1,
                            evidence_id_2=id2,
                            correlation_type=CorrelationType.HASH_MATCH,
                            confidence=0.99,
                            details={
                                'hash_type': 'sha256',
                                'hash_value': hash_val,
                                'duplicate_count': count
                            }
                        )
                        duplicates.append(correlation)
                        self.correlations.append(correlation)
                        
                        self.logger.info(f"Hash duplicate detected: {id1} == {id2}")
                        
                        # Create anomaly alert
                        alert = AnomalyAlert(
                            anomaly_type=AnomalyType.HASH_DUPLICATE,
                            anomaly_id=f"HASH_DUP_{id1}_{id2}",
                            description=f"Evidence items have identical SHA256 hash",
                            affected_items=[id1, id2],
                            severity="high",
                            timestamp=datetime.utcnow().isoformat() + 'Z',
                            context={
                                'hash': hash_val,
                                'duplicate_count': count
                            }
                        )
                        self.anomalies.append(alert)
            
        except Exception as e:
            self.logger.error(f"Hash duplicate detection failed: {e}")
        
        return duplicates
    
    def analyze_temporal_patterns(self, case_id: str) -> Dict[str, Any]:
        """
        Analyze temporal patterns in evidence acquisition
        Identifies timeline gaps, clusters, and anomalies
        """
        analysis = {
            'case_id': case_id,
            'total_events': 0,
            'date_range': None,
            'timeline_gaps': [],
            'temporal_clusters': [],
            'average_interval_seconds': 0,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        try:
            cursor = self.db.connection.cursor()
            
            # Get CoC entries sorted by timestamp
            cursor.execute("""
                SELECT timestamp, evidence_id, action
                FROM chain_of_custody
                WHERE evidence_id IN (SELECT evidence_id FROM evidence WHERE case_id = ?)
                ORDER BY timestamp
            """, (case_id,))
            
            events = cursor.fetchall()
            analysis['total_events'] = len(events)
            
            if len(events) < 2:
                return analysis
            
            # Calculate intervals between events
            timestamps = [datetime.fromisoformat(e[0].replace('Z', '+00:00')) for e in events]
            intervals = [
                (timestamps[i+1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps) - 1)
            ]
            
            if intervals:
                analysis['average_interval_seconds'] = statistics.mean(intervals)
                analysis['date_range'] = {
                    'start': timestamps[0].isoformat() + 'Z',
                    'end': timestamps[-1].isoformat() + 'Z',
                    'duration_seconds': (timestamps[-1] - timestamps[0]).total_seconds()
                }
            
            # Detect timeline gaps (intervals > 2x average)
            if intervals:
                mean_interval = statistics.mean(intervals)
                for i, interval in enumerate(intervals):
                    if interval > mean_interval * 2:
                        gap_alert = AnomalyAlert(
                            anomaly_type=AnomalyType.TIMELINE_GAP,
                            anomaly_id=f"TIMELINE_GAP_{case_id}_{i}",
                            description=f"Unusual gap in evidence timeline ({interval:.0f}s)",
                            affected_items=[events[i][1], events[i+1][1]],
                            severity="medium",
                            timestamp=datetime.utcnow().isoformat() + 'Z',
                            context={
                                'gap_seconds': interval,
                                'average_seconds': mean_interval
                            }
                        )
                        analysis['timeline_gaps'].append({
                            'from': events[i][0],
                            'to': events[i+1][0],
                            'gap_seconds': interval
                        })
                        self.anomalies.append(gap_alert)
            
            # Identify temporal clusters (events within short time)
            if len(events) >= 3:
                for i in range(len(intervals)):
                    if intervals[i] < 60:  # Less than 1 minute
                        analysis['temporal_clusters'].append({
                            'event_1': events[i][0],
                            'event_2': events[i+1][0],
                            'interval_seconds': intervals[i]
                        })
            
            self.logger.info(f"Temporal analysis for {case_id}: {analysis['total_events']} events")
            
        except Exception as e:
            self.logger.error(f"Temporal analysis failed: {e}")
        
        return analysis
    
    def detect_anomalies(self, case_id: str) -> List[AnomalyAlert]:
        """
        Comprehensive anomaly detection across all evidence
        """
        anomalies = []
        
        try:
            cursor = self.db.connection.cursor()
            
            # Get all evidence for case
            cursor.execute("""
                SELECT evidence_id, size_bytes, date_acquired, status, file_path
                FROM evidence
                WHERE case_id = ?
            """, (case_id,))
            
            evidence_items = cursor.fetchall()
            sizes = [e[1] for e in evidence_items if e[1] > 0]
            
            if not sizes:
                return anomalies
            
            # Identify large files (> 3 standard deviations from mean)
            if len(sizes) >= 3:
                mean_size = statistics.mean(sizes)
                stdev_size = statistics.stdev(sizes)
                threshold = mean_size + (3 * stdev_size)
                
                for e in evidence_items:
                    if e[1] > threshold:
                        alert = AnomalyAlert(
                            anomaly_type=AnomalyType.LARGE_FILE,
                            anomaly_id=f"LARGE_FILE_{e[0]}",
                            description=f"File size significantly larger than typical ({e[1]} bytes)",
                            affected_items=[e[0]],
                            severity="medium",
                            timestamp=datetime.utcnow().isoformat() + 'Z',
                            context={
                                'file_size': e[1],
                                'average_size': mean_size,
                                'threshold': threshold
                            }
                        )
                        anomalies.append(alert)
                        self.anomalies.append(alert)
            
            self.logger.info(f"Anomaly detection for {case_id}: {len(anomalies)} anomalies found")
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
        
        return anomalies
    
    def correlate_evidence(self, case_id: str) -> List[CorrelationLink]:
        """
        Correlate evidence items by various metrics
        """
        correlations = []
        
        try:
            # Detect hash duplicates
            hash_correlations = self.detect_hash_duplicates(case_id)
            correlations.extend(hash_correlations)
            
            # Detect temporal correlations (same source, similar timestamps)
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT e1.evidence_id, e2.evidence_id, e1.source, e2.source, 
                       e1.date_acquired, e2.date_acquired
                FROM evidence e1
                JOIN evidence e2 ON e1.case_id = e2.case_id 
                WHERE e1.case_id = ? AND e1.evidence_id < e2.evidence_id
                AND e1.source = e2.source
            """, (case_id,))
            
            same_source_pairs = cursor.fetchall()
            for pair in same_source_pairs:
                correlation = CorrelationLink(
                    evidence_id_1=pair[0],
                    evidence_id_2=pair[1],
                    correlation_type=CorrelationType.SAME_SOURCE,
                    confidence=0.95,
                    details={'source': pair[2]}
                )
                correlations.append(correlation)
                self.correlations.append(correlation)
            
            self.logger.info(f"Evidence correlation for {case_id}: {len(correlations)} correlations found")
            
        except Exception as e:
            self.logger.error(f"Evidence correlation failed: {e}")
        
        return correlations
    
    def generate_analytics_report(self, case_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report
        """
        report = {
            'case_id': case_id,
            'generated': datetime.utcnow().isoformat() + 'Z',
            'temporal_analysis': self.analyze_temporal_patterns(case_id),
            'anomalies': len(self.anomalies),
            'correlations': len(self.correlations),
            'anomaly_details': [
                {
                    'type': a.anomaly_type.value,
                    'id': a.anomaly_id,
                    'description': a.description,
                    'severity': a.severity,
                    'affected_items': a.affected_items
                }
                for a in self.anomalies[-10:]  # Last 10 anomalies
            ],
            'correlation_details': [
                {
                    'type': c.correlation_type.value,
                    'item_1': c.evidence_id_1,
                    'item_2': c.evidence_id_2,
                    'confidence': c.confidence,
                    'details': c.details
                }
                for c in self.correlations[-10:]  # Last 10 correlations
            ]
        }
        
        return report


_analytics_instance: Optional[AdvancedAnalytics] = None


def get_analytics() -> AdvancedAnalytics:
    """Factory function to get analytics singleton"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AdvancedAnalytics()
    return _analytics_instance
