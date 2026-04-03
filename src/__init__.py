"""
DFEPR - Digital Forensics Evidence Preservation & Recovery Lab
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "DFEPR Team"
__description__ = "Open-source forensic investigation lab"
__license__ = "ACPO Compliant"

# Import main modules
from src.chain_of_custody import ChainOfCustody, EvidenceRegistry, CustodyAction, CustodyEntry
from src.hash_verifier import HashVerifier, HashMatch
from src.file_recovery import FileRecoveryManager, RecoveredFile
from src.report_generator import ReportGenerator, InvestigationReport, CaseInfo
from src.utilities import (
    Logger, SystemHelper, FileHelper, ConfigHelper, 
    ValidationHelper, TimestampHelper
)
from src.logging_handler import (
    StructuredLogger, LogLevel, LogFormatter, OperationContext, get_logger
)
from src.config_manager import (
    ConfigurationManager, DFEPRConfig, get_config_manager,
    AcquisitionConfig, RecoveryConfig, ReportingConfig, 
    StorageConfig, ToolsConfig, ACPOConfig, SecurityConfig, ConfigProfile
)
from src.database import (
    DatabaseManager, get_database_manager, CaseRecord, EvidenceRecord, EvidenceStatus
)
from src.validator import (
    DataValidator, get_validator, ValidationResult, ValidationLevel
)
from src.statistics import (
    StatisticsCollector, get_statistics_collector, CaseStatistics, SystemStatistics
)
from src.recovery import (
    RecoveryManager, get_recovery_manager, RecoveryTool, RecoveryStatus, RecoveryTask,
    PhotoRecManager, ScalpelManager, TSKRecoveryManager
)

__all__ = [
    # Chain of Custody
    'ChainOfCustody',
    'EvidenceRegistry',
    'CustodyAction',
    'CustodyEntry',
    # Hash Management
    'HashVerifier',
    'HashMatch',
    # File Recovery
    'FileRecoveryManager',
    'RecoveredFile',
    # Reporting
    'ReportGenerator',
    'InvestigationReport',
    'CaseInfo',
    # Utilities
    'Logger',
    'SystemHelper',
    'FileHelper',
    'ConfigHelper',
    'ValidationHelper',
    'TimestampHelper',
    # Logging & Monitoring
    'StructuredLogger',
    'LogLevel',
    'LogFormatter',
    'OperationContext',
    'get_logger',
    # Configuration Management
    'ConfigurationManager',
    'DFEPRConfig',
    'get_config_manager',
    'AcquisitionConfig',
    'RecoveryConfig',
    'ReportingConfig',
    'StorageConfig',
    'ToolsConfig',
    'ACPOConfig',
    'SecurityConfig',
    'ConfigProfile',
    # Database Management
    'DatabaseManager',
    'get_database_manager',
    'CaseRecord',
    'EvidenceRecord',
    'EvidenceStatus',
    # Data Validation
    'DataValidator',
    'get_validator',
    'ValidationResult',
    'ValidationLevel',
    # Statistics & Analytics
    'StatisticsCollector',
    'get_statistics_collector',
    'CaseStatistics',
    'SystemStatistics',
    # File Recovery Operations
    'RecoveryManager',
    'get_recovery_manager',
    'RecoveryTool',
    'RecoveryStatus',
    'RecoveryTask',
    'PhotoRecManager',
    'ScalpelManager',
    'TSKRecoveryManager',
]
