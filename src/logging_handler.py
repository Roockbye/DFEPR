#!/usr/bin/env python3
"""
Advanced logging and monitoring for DFEPR operations.

Provides structured logging with timestamps, log levels, operation tracking,
and audit trail generation for ACPO compliance.

Author: DFEPR Development Team
License: GPL 3.0+
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
import sys


class LogLevel(Enum):
    """Log severity levels aligned with ACPO operation tracking."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    AUDIT = 25  # Custom level between INFO and WARNING


class LogFormatter(logging.Formatter):
    """Custom formatter for audit trail compliance."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'AUDIT': '\033[34m',      # Blue
        'RESET': '\033[0m'
    }

    def __init__(self, fmt=None, datefmt=None, use_color=True):
        """
        Initialize formatter.
        
        Args:
            fmt: Log format string
            datefmt: Date/time format
            use_color: Enable colored output
        """
        super().__init__(fmt, datefmt)
        self.use_color = use_color and sys.stdout.isatty()

    def format(self, record):
        """Format log record with colors and structured data."""
        # Add color if enabled
        if self.use_color:
            levelname_color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{levelname_color}{record.levelname}{reset}"

        # Format timestamp in ISO 8601 format
        record.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        return super().format(record)


class StructuredLogger:
    """
    Structured logging system for DFEPR operations.
    
    Provides audit-compliant logging with operation tracking, evidence
    linking, and forensic chain of custody integration.
    """

    def __init__(self, name: str, log_dir: Optional[Path] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically module name)
            log_dir: Directory for log files (default: ./logs)
        """
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path('./logs')
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LogLevel.DEBUG.value)

        # Add 'AUDIT' level
        logging.addLevelName(LogLevel.AUDIT.value, 'AUDIT')

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LogLevel.INFO.value)
        console_formatter = LogFormatter(
            fmt='%(timestamp)s [%(levelname)-8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            use_color=True
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (DEBUG and above) - rotated daily
        log_file = self.log_dir / f'{name}.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=10
        )
        file_handler.setLevel(LogLevel.DEBUG.value)
        file_formatter = LogFormatter(
            fmt='%(timestamp)s [%(levelname)-8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            use_color=False
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Audit log handler (AUDIT level and above)
        audit_log = self.log_dir / f'{name}_audit.jsonl'
        self.audit_handler = logging.FileHandler(audit_log, mode='a')
        self.audit_handler.setLevel(LogLevel.AUDIT.value)
        self.audit_formatter = LogFormatter(
            fmt='%(timestamp)s [%(levelname)-8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            use_color=False
        )
        self.audit_handler.setFormatter(self.audit_formatter)
        self.logger.addHandler(self.audit_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self.logger.debug(message, extra=self._format_extra(kwargs))

    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self.logger.info(message, extra=self._format_extra(kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self.logger.warning(message, extra=self._format_extra(kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self.logger.error(message, extra=self._format_extra(kwargs))

    def critical(self, message: str, **kwargs):
        """Log critical message with optional context."""
        self.logger.critical(message, extra=self._format_extra(kwargs))

    def audit(self, operation: str, case_id: str, evidence_id: str,
              action: str, result: str, **details):
        """
        Log audit trail entry for ACPO compliance.
        
        Args:
            operation: Type of operation (acquire, recover, verify, etc.)
            case_id: Associated case identifier
            evidence_id: Associated evidence identifier
            action: Specific action taken
            result: Result of action (success, warning, error, etc.)
            **details: Additional context (user, tool, hash, etc.)
        """
        audit_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'operation': operation,
            'case_id': case_id,
            'evidence_id': evidence_id,
            'action': action,
            'result': result,
            **details
        }
        self.logger.log(
            LogLevel.AUDIT.value,
            json.dumps(audit_entry, default=str)
        )

    def log_operation_start(self, operation: str, case_id: str = None, **context):
        """Log operation start with context."""
        context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ''
        msg = f"Starting {operation}" + (f": {context_str}" if context_str else "")
        if case_id:
            self.audit(operation, case_id, '', 'START', 'initiated', **context)
        else:
            self.info(msg, **context)

    def log_operation_end(self, operation: str, case_id: str = None, 
                          success: bool = True, **context):
        """Log operation completion with results."""
        result = "completed" if success else "failed"
        status = "success" if success else "error"
        context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ''
        msg = f"{operation} {result}" + (f": {context_str}" if context_str else "")
        
        if case_id:
            self.audit(operation, case_id, '', 'COMPLETE', status, **context)
        else:
            level = logging.INFO if success else logging.ERROR
            self.logger.log(level, msg)

    def _format_extra(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format extra context data for structured logging."""
        if not data:
            return {}
        return {'extra': data}

    @property
    def audit_log_path(self) -> Path:
        """Get path to audit log file."""
        return self.log_dir / f'{self.name}_audit.jsonl'

    def get_audit_trail(self, case_id: str = None) -> list:
        """
        Retrieve audit trail entries, optionally filtered by case.
        
        Args:
            case_id: Optional case ID to filter by
            
        Returns:
            List of audit trail entries as dictionaries
        """
        entries = []
        audit_log = self.audit_log_path
        
        if not audit_log.exists():
            return entries

        try:
            with open(audit_log, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    # Parse JSON audit entry
                    try:
                        # Extract JSON from log format
                        if '[AUDIT]' in line:
                            json_str = line.split('[AUDIT]', 1)[1].strip()
                        else:
                            # Try to find JSON objects in line
                            import re
                            json_match = re.search(r'\{.*\}', line)
                            if json_match:
                                json_str = json_match.group()
                            else:
                                continue
                        
                        entry = json.loads(json_str)
                        
                        # Filter by case_id if specified
                        if case_id is None or entry.get('case_id') == case_id:
                            entries.append(entry)
                    except (json.JSONDecodeError, IndexError):
                        continue
        except Exception as e:
            self.error(f"Error reading audit trail: {e}")

        return entries

    def export_audit_trail(self, output_file: Path, case_id: str = None):
        """
        Export audit trail to file.
        
        Args:
            output_file: Path to export to
            case_id: Optional case ID to filter by
        """
        entries = self.get_audit_trail(case_id)
        
        with open(output_file, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')
        
        self.info(f"Exported {len(entries)} audit entries to {output_file}")


class OperationContext:
    """Context manager for tracking operations with logging."""

    def __init__(self, logger: StructuredLogger, operation: str, 
                 case_id: str = None, **context):
        """
        Initialize operation context.
        
        Args:
            logger: StructuredLogger instance
            operation: Operation name
            case_id: Associated case ID
            **context: Additional context data
        """
        self.logger = logger
        self.operation = operation
        self.case_id = case_id
        self.context = context
        self.start_time = None

    def __enter__(self):
        """Start operation tracking."""
        self.start_time = datetime.now(timezone.utc)
        self.logger.log_operation_start(self.operation, self.case_id, **self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End operation tracking."""
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        success = exc_type is None
        
        context_with_duration = {**self.context, 'duration_seconds': duration}
        self.logger.log_operation_end(
            self.operation,
            self.case_id,
            success=success,
            **context_with_duration
        )
        
        if exc_type is not None:
            self.logger.error(
                f"Operation {self.operation} failed: {exc_val}",
                error_type=exc_type.__name__
            )
        
        return False  # Propagate exceptions


# Module-level logger instance
_default_logger = None


def get_logger(name: str = 'dfepr') -> StructuredLogger:
    """
    Get or create default logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = StructuredLogger(name)
    return _default_logger


if __name__ == '__main__':
    # Example usage
    logger = StructuredLogger('dfepr_test')
    
    # Test different log levels
    logger.debug("Debug message", module='test')
    logger.info("Information message", module='test')
    logger.warning("Warning message", module='test')
    logger.error("Error message", module='test')
    
    # Test audit logging
    logger.audit(
        operation='test_acquire',
        case_id='CASE-2024-001',
        evidence_id='EV-001',
        action='acquire_disk',
        result='success',
        device='/dev/sda',
        size_gb=100
    )
    
    # Test operation context
    with OperationContext(logger, 'test_operation', 'CASE-2024-001', user='analyst'):
        logger.info("Operation in progress")
    
    print(f"\n✓ Logging infrastructure initialized")
    print(f"  Audit log: {logger.audit_log_path}")
