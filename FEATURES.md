# DFEPR Features Guide

## Overview

This document describes the complete feature set of the DFEPR (Digital Forensics Evidence Preservation & Recovery Lab), an open-source forensic investigation platform built for ACPO compliance.

## Core Features

### 1. Chain of Custody Management

**Purpose**: Track complete evidence handling from acquisition through analysis to final disposition.

**Key Features**:
- Automated entry tracking with timestamps
- Personnel accountability (name, title, location)
- Action categorization (acquisition, transfer, analysis, storage, release)
- Digital signature support for legal admissibility
- JSON and CSV export formats for reporting
- Complete audit trail for ACPO Principle 2

**Usage**:
```python
from src import ChainOfCustody, CustodyAction

coc = ChainOfCustody("CASE-2024-001", "EV-001")
coc.add_entry(
    action=CustodyAction.ACQUISITION,
    person_name="John Analyst",
    person_title="Principal Analyst",
    location="Lab A",
    description="Disk image acquisition",
    items_affected=["device:/dev/sda"],
    signature="JA_2024-04-03"
)
```

### 2. Cryptographic Hash Verification

**Purpose**: Ensure digital evidence integrity through cryptographic checksums.

**Key Features**:
- Multi-algorithm support (MD5, SHA1, SHA256, SHA512)
- Batch file verification
- Hash registration and comparison
- Verification logging with pass/fail/mismatch tracking
- Performance optimization with rotating file algorithms
- Complete audit trail for ACPO Principle 1

**Supported Algorithms**:
- MD5 (legacy, not recommended for legal use)
- SHA1 (deprecated, NIST not recommended)
- SHA256 (recommended, FIPS 180-4)
- SHA512 (maximum security, FIPS 180-4)

**Usage**:
```python
from src import HashVerifier

verifier = HashVerifier("CASE-2024-001")
hashes = verifier.calculate_hash("evidence.img", 
                                 algorithms=["sha256", "md5"])
is_valid, actual = verifier.verify_file_hash("evidence.img", 
                                              expected_hash, 
                                              "sha256")
```

### 3. File Recovery

**Purpose**: Recover deleted and hidden files from forensic images.

**Key Features**:
- PhotoRec integration (signature-based carving)
- Scalpel integration (advanced carving with configuration)
- The Sleuth Kit (TSK) integration (inode-based recovery)
- Recovered file tracking and registration
- Carving depth control
- File type prioritization

**Recovery Methods**:

#### PhotoRec
- Signature-based file carving
- No file system dependency
- Best for unknown file types
- Automatic file type detection

#### Scalpel
- Advanced carving with configurable patterns
- Custom file type definitions
- Database-aware carving
- Performance optimized

#### TSK
- Inode-based file listing
- File system aware
- Fast metadata recovery
- Filesystem journal analysis

**Usage**:
```python
from src import FileRecoveryManager, RecoveredFile

recovery = FileRecoveryManager("CASE-2024-001", image_path="disk.img")
recovered = recovery.recover_photorec(output_dir="./recovered")
for file in recovered:
    print(f"Recovered: {file.filename} ({file.size} bytes)")
```

### 4. Report Generation

**Purpose**: Generate court-admissible forensic investigation reports.

**Key Features**:
- Multiple export formats (Text, HTML, JSON)
- Case information tracking
- Investigation findings documentation
- Evidence summary integration
- Hash verification results inclusion
- Digital signatures and timestamps
- Customizable report sections

**Export Formats**:
- **Text**: Plain text with formatted sections for printing/filing
- **HTML**: Web-viewable with styling and navigation
- **JSON**: Machine-readable for analysis and re-reporting

**Usage**:
```python
from src import ReportGenerator, InvestigationReport, CaseInfo

case = CaseInfo(
    case_id="CASE-2024-001",
    description="Data theft investigation",
    investigator_name="John Analyst"
)

report = InvestigationReport(...)
generator = ReportGenerator("CASE-2024-001")
generator.generate_html_report(report, "report.html")
```

### 5. Advanced Logging & Monitoring

**Purpose**: Provide ACPO-compliant operational audit trail.

**Key Features**:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL, AUDIT)
- Structured JSON audit entries
- Rotating file handlers with automatic backups
- Console output with color coding
- Operation context tracking (duration, result)
- Case and evidence linkage
- Audit trail export and filtering

**Log Levels**:
- **DEBUG**: Detailed technical information
- **INFO**: General information messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical conditions
- **AUDIT**: ACPO audit trail entries (custom level)

**Features**:
- Thread-safe file operations
- Automatic log rotation (20MB files, 10 backups)
- ISO 8601 UTC timestamps (timezone-aware)
- Colored console output
- JSON-formatted audit logs
- Audit trail filtering by case_id

**Usage**:
```python
from src import get_logger, OperationContext

logger = get_logger('dfepr.acquisition')

# Simple logging
logger.info("Starting acquisition", device="/dev/sda")

# Audit logging
logger.audit(
    operation='disk_acquisition',
    case_id='CASE-2024-001',
    evidence_id='EV-001',
    action='acquire',
    result='success',
    device='/dev/sda'
)

# Operation tracking
with OperationContext(logger, 'analyze_image', 'CASE-2024-001'):
    # Operations tracked with automatic timing
    pass
```

### 6. Configuration Management

**Purpose**: Manage lab settings across multiple operational profiles.

**Key Features**:
- Profile-based configuration (development, testing, production, training)
- YAML file persistence
- Environment variable overrides
- Default configuration values
- Configuration validation with error reporting
- Case directory structure creation
- Persistent storage in ~/.dfepr/config/

**Configuration Profiles**:

#### Development
- Relaxed verification
- Debug logging enabled
- Local file storage
- All tools optional

#### Testing
- Full verification
- Mock tool outputs
- Test evidence directories
- Performance monitoring enabled

#### Production
- Strict ACPO compliance
- All verification required
- All tools mandatory
- Audit logging required

#### Training
- Detailed logging
- Sample data provided
- Reduced performance requirements
- Educational notes included

**Configuration Sections**:

1. **Acquisition Settings**
   - Write-block requirement
   - Error recovery
   - Hash algorithm
   - Chunk size

2. **Recovery Settings**
   - Tool enablement
   - Carving depth
   - File type priorities

3. **Reporting Settings**
   - Export formats
   - Content inclusion flags

4. **Storage Settings**
   - Directory paths
   - Backup frequency
   - Auto-cleanup policy

5. **Tools Settings**
   - Paths to forensic tools
   - Availability checking

6. **ACPO Settings**
   - Principle enforcement
   - Case ID format
   - Audit requirements

7. **Security Settings**
   - Authentication
   - Encryption
   - Session timeouts

**Usage**:
```python
from src import get_config_manager

config_mgr = get_config_manager()
config_mgr.load_profile('production')

# Access sections
acq_config = config_mgr.config.acquisition
print(f"Hash algorithm: {acq_config.hash_algorithm}")

# Update configuration
config_mgr.set_section('acquisition', {
    'write_block': True,
    'verify_after_imaging': True
})

# Save custom profile
config_mgr.save_profile('custom_production')
```

### 7. Command-Line Interface (CLI)

**Purpose**: Professional command-line interface for DFEPR operations.

**Features**:
- 6 command groups with 17+ subcommands
- Input validation and error handling
- ACPO compliance checking
- Progress indicators
- Verbose and quiet modes
- Batch operations support

**Command Groups**:

#### case Group
```bash
dfepr case create --case-id CASE-2024-001 --description "Investigation"
dfepr case list [--active] [--archived]
```

#### evidence Group
```bash
dfepr evidence register --case-id CASE-2024-001 --evidence-id EV-001
dfepr evidence coc-add --evidence-id EV-001 --action acquisition
dfepr evidence coc-report --evidence-id EV-001 [--format json|text|csv]
```

#### hash Group
```bash
dfepr hash calculate --file evidence.img [--algorithms md5,sha256,sha512]
dfepr hash verify --file evidence.img --hash ABC123... [--algorithm sha256]
```

#### recovery Group
```bash
dfepr recovery photorec --image disk.img --output recovered/
dfepr recovery scalpel --image disk.img --output recovered/
```

#### report Group
```bash
dfepr report generate --case-id CASE-2024-001 [--format html]
dfepr report export-audit --case-id CASE-2024-001 [--output audit.jsonl]
```

#### tools Group
```bash
dfepr tools check [--all]
dfepr tools info [--system] [--forensic]
```

## Integration Features

### ACPO Compliance

All features implement ACPO (Association of Chief Police Officers) guidelines:

- **Principle 1**: No modification of original data
  - Write-blocking enforcement
  - Hash verification for integrity
  - Forensic imaging best practices

- **Principle 2**: Chain of custody
  - Complete operation tracking
  - Personnel accountability
  - Digital signatures support

- **Principle 3**: Documentation
  - Automated procedure logging
  - Report generation (text, HTML, JSON)
  - Audit trail with timestamps

- **Principle 4**: Oversight
  - Senior manager approval workflow (planned)
  - Case tracking and status
  - Complete auditability

### Standards Compliance

- **ISO/IEC 27037:2012**: Digital evidence identification
- **ISO/IEC 27041:2015**: Guidance for preservation
- **ISO/IEC 27042:2015**: Analysis and interpretation
- **NIST SP 800-86**: Legal and technical guidelines

## Utility Functions

### FileHelper
- Path validation and normalization
- Recursive directory operations
- Safe file operations
- Disk space verification

### SystemHelper
- System information retrieval
- Tool availability checking
- Process management
- Resource monitoring

### ValidationHelper
- ACPO case ID validation
- Hash format validation
- File path validation
- Configuration validation

### TimestampHelper
- UTC timestamp generation
- ISO 8601 formatting
- Timezone handling
- Timestamp comparison

## API Examples

### Complete Investigation Workflow

```python
from src import (
    ChainOfCustody, CustodyAction,
    HashVerifier,
    FileRecoveryManager,
    ReportGenerator, InvestigationReport, CaseInfo,
    get_logger, OperationContext,
    get_config_manager
)

# Initialize
logger = get_logger('forensic_investigation')
config = get_config_manager()
config.load_profile('production')

# Create case paths
case_id = "CASE-2024-001"
case_paths = config.create_case_paths(case_id)

with OperationContext(logger, 'complete_investigation', case_id):
    # 1. Document acquisition
    coc = ChainOfCustody(case_id, str(case_paths['metadata']))
    coc.add_entry(
        action=CustodyAction.ACQUISITION,
        person_name="Analyst",
        person_title="Forensic Analyst",
        location="Lab",
        description="Disk acquisition",
        items_affected=["device:/dev/sda"]
    )
    
    # 2. Verify integrity
    verifier = HashVerifier(case_id, str(case_paths['metadata']))
    hashes = verifier.calculate_hash("image.dd")
    verifier.register_hash("EV-001", "image.dd", hashes)
    
    # 3. Recover files (if deleted)
    recovery = FileRecoveryManager(case_id, "image.dd")
    recovered = recovery.recover_photorec(str(case_paths['recovered']))
    
    # 4. Generate report
    case_info = CaseInfo(case_id, "Investigation description")
    report = InvestigationReport(case_info, coc, verifier, recovered)
    generator = ReportGenerator(case_id, str(case_paths['reports']))
    generator.generate_html_report(report, "investigation_report.html")
```

## Security Features

- **No data modification**: Write-block enforcement
- **Cryptographic verification**: SHA256/SHA512 hashing
- **Operation tracking**: Audit trail with timestamps
- **Access control**: (Planned for v2)
- **Encryption support**: (Planned for v2)
- **Session management**: (Planned for v2)

## Performance Notes

- Hash calculation: ~1 GB/second (SHA256)
- File recovery: Depends on image size and method
- Report generation: < 5 seconds for typical investigations
- Log operations: Minimal overhead with rotating files

## Troubleshooting

### Common Issues

1. **Tool not found**: Check tool installation
   ```bash
   dfepr tools check
   ```

2. **Permission denied**: Ensure write access to evidence directories
   ```bash
   ls -la evidence/
   ```

3. **Hash mismatch**: Verify image integrity
   ```bash
   dfepr hash verify --file image.dd --hash ABC... --algorithm sha256
   ```

4. **Log file location**: Check default log directory
   ```bash
   ls logs/
   ```

## Future Enhancements

- Database backend for case persistence (SQLite)
- Timeline generation from file metadata
- Evidence correlation engine
- Machine learning file categorization
- Web-based dashboard
- Multi-user collaboration
- Role-based access control
- GPU-accelerated hash calculation
- Cloud integration
- Mobile evidence acquisition support

## Support and Documentation

- **User Guide**: [README.md](README.md)
- **ACPO Guidelines**: [docs/ACPO_Guidelines.md](docs/ACPO_Guidelines.md)
- **Procedures**: [docs/procedures/](docs/procedures/)
- **FAQ**: [FAQ.md](FAQ.md)
- **Case Examples**: [docs/case_examples/](docs/case_examples/)

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2024-04-03
- **Last Updated**: 2024-04-03
- **License**: GPL 3.0+
