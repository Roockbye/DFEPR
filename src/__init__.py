"""
DFEPR - Digital Forensics Evidence Preservation & Recovery Lab
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "DFEPR Team"
__description__ = "Open-source forensic investigation lab"

# Import main modules
from src.chain_of_custody import ChainOfCustody, EvidenceRegistry
from src.hash_verifier import HashVerifier, HashMatch
from src.file_recovery import FileRecoveryManager
from src.report_generator import ReportGenerator, InvestigationReport, CaseInfo

__all__ = [
    'ChainOfCustody',
    'EvidenceRegistry',
    'HashVerifier',
    'HashMatch',
    'FileRecoveryManager',
    'ReportGenerator',
    'InvestigationReport',
    'CaseInfo'
]
