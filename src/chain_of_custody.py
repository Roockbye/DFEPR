#!/usr/bin/env python3
"""
DFEPR - Chain of Custody Management
Manages the complete chain of custody for digital forensic evidence
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class CustodyAction(Enum):
    """Types of custody actions"""
    ACQUISITION = "acquisition"
    TRANSFER_TO = "transfer_to"
    TRANSFER_FROM = "transfer_from"
    ANALYSIS = "analysis"
    STORAGE = "storage"
    RELEASE = "release"

@dataclass
class CustodyEntry:
    """Single entry in chain of custody"""
    timestamp: str
    action: str
    person_name: str
    person_title: str
    location: str
    description: str
    items_affected: str  # JSON list
    signature: str
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ChainOfCustody:
    """Manages chain of custody records for evidence"""
    
    def __init__(self, case_id: str, evidence_id: str, storage_dir: str = "evidence/cases"):
        """
        Initialize chain of custody record
        
        Args:
            case_id: Case identifier
            evidence_id: Evidence identifier
            storage_dir: Base directory for storage
        """
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[CustodyEntry] = []
        self.file_path = self.storage_dir / f"{evidence_id}_coc.json"
        self.csv_path = self.storage_dir / f"{evidence_id}_coc.csv"
        
        # Load existing records if file exists
        if self.file_path.exists():
            self._load_records()
    
    def add_entry(
        self,
        action: CustodyAction,
        person_name: str,
        person_title: str,
        location: str,
        description: str,
        items_affected: List[str],
        signature: str = "",
        notes: str = ""
    ) -> None:
        """
        Add an entry to the chain of custody
        
        Args:
            action: Type of action
            person_name: Name of person
            person_title: Title/role of person
            location: Location where action occurred
            description: Description of action
            items_affected: List of items affected
            signature: Digital or handwritten signature reference
            notes: Additional notes
        """
        entry = CustodyEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            action=action.value,
            person_name=person_name,
            person_title=person_title,
            location=location,
            description=description,
            items_affected=json.dumps(items_affected),
            signature=signature,
            notes=notes
        )
        
        self.entries.append(entry)
        self._save_records()
    
    def _save_records(self) -> None:
        """Save records to JSON file"""
        data = {
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "created": datetime.utcnow().isoformat() + "Z",
            "entries": [entry.to_dict() for entry in self.entries]
        }
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save as CSV for easy viewing
        self._save_csv()
    
    def _save_csv(self) -> None:
        """Export records to CSV"""
        if not self.entries:
            return
        
        with open(self.csv_path, 'w', newline='') as f:
            fieldnames = [
                'timestamp', 'action', 'person_name', 'person_title',
                'location', 'description', 'items_affected', 'signature', 'notes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for entry in self.entries:
                row = entry.to_dict()
                # Keep items_affected as JSON string in CSV
                writer.writerow(row)
    
    def _load_records(self) -> None:
        """Load records from JSON file"""
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            self.entries = [
                CustodyEntry(**entry) for entry in data.get('entries', [])
            ]
    
    def get_history(self) -> List[Dict]:
        """Get complete custody history"""
        return [entry.to_dict() for entry in self.entries]
    
    def generate_report(self) -> str:
        """Generate formatted chain of custody report"""
        report = f"""
================================================================================
CHAIN OF CUSTODY REPORT
================================================================================

Case ID:      {self.case_id}
Evidence ID:  {self.evidence_id}
Report Date:  {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

================================================================================
CUSTODY HISTORY
================================================================================

"""
        
        if not self.entries:
            report += "No entries recorded.\n"
            return report
        
        for idx, entry in enumerate(self.entries, 1):
            items = json.loads(entry.items_affected)
            report += f"""
--- Entry {idx} ---
Timestamp:    {entry.timestamp}
Action:       {entry.action.upper()}
Person:       {entry.person_name} ({entry.person_title})
Location:     {entry.location}
Description:  {entry.description}
Items:        {', '.join(items)}
Signature:    {entry.signature}
Notes:        {entry.notes if entry.notes else 'N/A'}

"""
        
        report += """
================================================================================
CERTIFICATION
================================================================================

I hereby certify that the above information is accurate and complete regarding
the chain of custody for the specified evidence. I maintain responsibility for
the proper handling and security of these items.

Authorized Lab Manager:  ________________________

Signature:               ________________________

Date:                    ________________________

================================================================================
"""
        
        return report
    
    def export_for_submission(self, output_path: str) -> bool:
        """
        Export chain of custody in format suitable for legal submission
        
        Args:
            output_path: Path to save report
            
        Returns:
            True if successful
        """
        try:
            report = self.generate_report()
            with open(output_path, 'w') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False


class EvidenceRegistry:
    """Central registry of all evidence in the laboratory"""
    
    def __init__(self, storage_dir: str = "evidence/cases"):
        """Initialize evidence registry"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.storage_dir / "evidence_registry.json"
        self.evidence: Dict[str, Dict] = {}
        
        if self.registry_file.exists():
            self._load_registry()
    
    def register_evidence(
        self,
        evidence_id: str,
        case_id: str,
        description: str,
        source: str,
        hash_md5: str,
        hash_sha256: str,
        acquirer: str = "Unknown"
    ) -> bool:
        """
        Register new evidence
        
        Args:
            evidence_id: Unique evidence identifier
            case_id: Case identifier
            description: Description of evidence
            source: Source of evidence
            hash_md5: MD5 hash
            hash_sha256: SHA256 hash
            acquirer: Person who acquired evidence
            
        Returns:
            True if successful
        """
        if evidence_id in self.evidence:
            print(f"Error: Evidence {evidence_id} already registered")
            return False
        
        self.evidence[evidence_id] = {
            "case_id": case_id,
            "description": description,
            "source": source,
            "hashes": {
                "md5": hash_md5,
                "sha256": hash_sha256
            },
            "acquirer": acquirer,
            "registered_date": datetime.utcnow().isoformat() + "Z",
            "status": "registered",
            "coc_file": f"{evidence_id}_coc.json"
        }
        
        self._save_registry()
        return True
    
    def _save_registry(self) -> None:
        """Save registry to file"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
    
    def _load_registry(self) -> None:
        """Load registry from file"""
        with open(self.registry_file, 'r') as f:
            self.evidence = json.load(f)
    
    def get_case_evidence(self, case_id: str) -> List[str]:
        """Get all evidence for a case"""
        return [
            eid for eid, data in self.evidence.items()
            if data.get("case_id") == case_id
        ]
    
    def generate_summary(self) -> str:
        """Generate registry summary"""
        summary = """
================================================================================
EVIDENCE REGISTRY SUMMARY
================================================================================

Generated: {}

Total Evidence Items: {}

Cases in Registry:
""".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), len(self.evidence))
        
        cases = {}
        for eid, data in self.evidence.items():
            case_id = data.get("case_id", "Unknown")
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(eid)
        
        for case_id, evidence_list in sorted(cases.items()):
            summary += f"\n  {case_id}: {len(evidence_list)} items\n"
            
            for eid in evidence_list:
                data = self.evidence[eid]
                summary += f"    - {eid}: {data.get('description', 'N/A')}\n"
                summary += f"      MD5: {data['hashes']['md5'][:16]}...\n"
        
        summary += "\n" + "="*80 + "\n"
        return summary


# Example usage
if __name__ == "__main__":
    # Create a case and evidence
    case_id = "THEFT_2026_000001"
    evidence_id = f"{case_id}_001"
    
    # Initialize chain of custody
    coc = ChainOfCustody(case_id, evidence_id)
    
    # Add acquisition entry
    coc.add_entry(
        action=CustodyAction.ACQUISITION,
        person_name="John Doe",
        person_title="Forensic Examiner",
        location="Digital Lab - Room 101",
        description="Bitwise image acquisition of suspect hard drive",
        items_affected=["/dev/sda - 1TB Samsung HDD"],
        signature="JD-2026040301"
    )
    
    # Add analysis entry
    coc.add_entry(
        action=CustodyAction.ANALYSIS,
        person_name="Jane Smith",
        person_title="Senior Analyst",
        location="Digital Lab - Room 102",
        description="Initial forensic analysis - file recovery",
        items_affected=[evidence_id],
        signature="JS-2026040302",
        notes="Recovered 250 JPEG files from unallocated space"
    )
    
    # Print report
    print(coc.generate_report())
    
    # Export for submission
    coc.export_for_submission(f"evidence/cases/{evidence_id}_report.txt")
    
    # Registry example
    registry = EvidenceRegistry()
    registry.register_evidence(
        evidence_id=evidence_id,
        case_id=case_id,
        description="Suspect Hard Drive - 1TB Samsung",
        source="/dev/sda",
        hash_md5="a1b2c3d4e5f6g7h8i9j0",
        hash_sha256="1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
        acquirer="John Doe"
    )
    
    print("\nRegistry Summary:")
    print(registry.generate_summary())
