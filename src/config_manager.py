#!/usr/bin/env python3
"""
Configuration management for DFEPR operations.

Manages lab settings, case configurations, and tool preferences with
YAML persistence, environment variable support, and profile management.

Author: DFEPR Development Team
License: GPL 3.0+
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import yaml


class ConfigProfile(Enum):
    """Configuration profiles for different operational contexts."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    TRAINING = "training"


@dataclass
class AcquisitionConfig:
    """Disk acquisition settings."""
    write_block: bool = True
    error_recovery: bool = True
    verify_after_imaging: bool = True
    hash_algorithm: str = "SHA256"
    metadata_capture: bool = True
    sector_size: int = 512
    chunk_size_mb: int = 64
    timeout_seconds: int = 3600


@dataclass
class RecoveryConfig:
    """File recovery settings."""
    enable_photorec: bool = True
    enable_scalpel: bool = True
    enable_tsk: bool = True
    carving_depth: int = 0  # 0 = all, depth in sectors
    metadata_recovery: bool = True
    file_type_priorities: List[str] = field(
        default_factory=lambda: ["office", "images", "videos", "archives"]
    )


@dataclass
class ReportingConfig:
    """Report generation settings."""
    formats: List[str] = field(default_factory=lambda: ["text", "html", "json"])
    include_timeline: bool = True
    include_recovered_files: bool = True
    include_hash_verification: bool = True
    signature_required: bool = False
    digital_signature: bool = False


@dataclass
class StorageConfig:
    """Storage and paths configuration."""
    base_evidence_dir: str = "./evidence"
    log_dir: str = "./logs"
    temp_dir: str = "/tmp/dfepr"
    archive_dir: str = "./archived_cases"
    backup_count: int = 10
    auto_cleanup_temp: bool = True
    cleanup_age_days: int = 30


@dataclass
class ToolsConfig:
    """External forensic tools configuration."""
    ddrescue_path: str = "ddrescue"
    photorec_path: str = "photorec"
    scalpel_path: str = "scalpel"
    fls_path: str = "fls"
    icat_path: str = "icat"
    md5sum_path: str = "md5sum"
    sha256sum_path: str = "sha256sum"
    ensure_availability: bool = True


@dataclass
class ACPOConfig:
    """ACPO compliance settings."""
    principle_1_enabled: bool = True  # No modification
    principle_2_enabled: bool = True  # Chain of custody
    principle_3_enabled: bool = True  # Documentation
    principle_4_enabled: bool = True  # Senior manager oversight
    case_id_format: str = "CASE-{year}-{seq:04d}"
    require_case_description: bool = True
    require_investigator_details: bool = True
    audit_log_required: bool = True
    hash_verification_required: bool = True


@dataclass
class SecurityConfig:
    """Security and access control."""
    require_authentication: bool = False
    min_password_length: int = 12
    log_sensitive_data: bool = False
    encrypt_at_rest: bool = False
    encryption_key_file: Optional[str] = None
    session_timeout_minutes: int = 60


@dataclass
class DFEPRConfig:
    """Complete DFEPR configuration."""
    profile: str = ConfigProfile.PRODUCTION.value
    version: str = "1.0.0"
    
    # Sub-configurations
    acquisition: AcquisitionConfig = field(default_factory=AcquisitionConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    acpo: ACPOConfig = field(default_factory=ACPOConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)


class ConfigurationManager:
    """
    Manages DFEPR configuration with YAML persistence and environment overrides.
    
    Supports:
    - Multiple configuration profiles
    - YAML file persistence
    - Environment variable overrides
    - Configuration validation
    - Default values and schema
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Configuration directory (default: ~/.dfepr/config)
        """
        self.config_dir = config_dir or Path.home() / '.dfepr' / 'config'
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Current configuration
        self.config: DFEPRConfig = DFEPRConfig()
        
        # Configuration file paths
        self.profiles_dir = self.config_dir / 'profiles'
        self.profiles_dir.mkdir(exist_ok=True, parents=True)
        
        # Environment variable prefix
        self.env_prefix = 'DFEPR_'
        
        # Load default configuration
        self._load_defaults()

    def _load_defaults(self):
        """Load default configuration."""
        self.config = DFEPRConfig()

    def load_profile(self, profile: str = None) -> bool:
        """
        Load a configuration profile.
        
        Args:
            profile: Profile name (development, testing, production, training)
                    If None, loads from environment or uses PRODUCTION
                    
        Returns:
            True if profile loaded successfully, False otherwise
        """
        if profile is None:
            profile = os.getenv(f'{self.env_prefix}PROFILE', 
                               ConfigProfile.PRODUCTION.value)
        
        profile_file = self.profiles_dir / f'{profile}.yaml'
        
        if not profile_file.exists():
            # Return defaults if profile doesn't exist
            self._load_defaults()
            self.config.profile = profile
            return False
        
        try:
            with open(profile_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            self._load_from_dict(data)
            self.config.profile = profile
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            return True
        except Exception as e:
            print(f"Error loading profile {profile}: {e}")
            return False

    def _load_from_dict(self, data: Dict[str, Any]):
        """Load configuration from dictionary."""
        try:
            if 'acquisition' in data:
                self.config.acquisition = AcquisitionConfig(**data['acquisition'])
            if 'recovery' in data:
                self.config.recovery = RecoveryConfig(**data['recovery'])
            if 'reporting' in data:
                self.config.reporting = ReportingConfig(**data['reporting'])
            if 'storage' in data:
                self.config.storage = StorageConfig(**data['storage'])
            if 'tools' in data:
                self.config.tools = ToolsConfig(**data['tools'])
            if 'acpo' in data:
                self.config.acpo = ACPOConfig(**data['acpo'])
            if 'security' in data:
                self.config.security = SecurityConfig(**data['security'])
            
            if 'profile' in data:
                self.config.profile = data['profile']
            if 'version' in data:
                self.config.version = data['version']
        except TypeError as e:
            print(f"Warning: Configuration field mismatch: {e}")

    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_keys = [key for key in os.environ.keys() if key.startswith(self.env_prefix)]
        
        for env_key in env_keys:
            # Extract configuration path from env key
            # DFEPR_ACQUISITION_WRITE_BLOCK -> acquisition.write_block
            parts = env_key[len(self.env_prefix):].lower().split('_', 1)
            if len(parts) != 2:
                continue
            
            section, key = parts
            value = os.environ[env_key]
            
            # Parse boolean values
            if value.lower() in ('true', 'yes', '1'):
                value = True
            elif value.lower() in ('false', 'no', '0'):
                value = False
            elif value.isdigit():
                value = int(value)
            
            # Apply override
            self._set_config_value(section, key, value)

    def _set_config_value(self, section: str, key: str, value: Any):
        """Set a configuration value."""
        section_obj = getattr(self.config, section, None)
        if section_obj and hasattr(section_obj, key):
            setattr(section_obj, key, value)

    def save_profile(self, profile: str = None) -> bool:
        """
        Save current configuration as a profile.
        
        Args:
            profile: Profile name to save (default: current profile)
            
        Returns:
            True if saved successfully
        """
        if profile is None:
            profile = self.config.profile
        
        profile_file = self.profiles_dir / f'{profile}.yaml'
        
        try:
            config_dict = asdict(self.config)
            
            with open(profile_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            print(f"Error saving profile {profile}: {e}")
            return False

    def get_config(self) -> DFEPRConfig:
        """Get current configuration."""
        return self.config

    def get_section(self, section: str) -> Optional[Any]:
        """Get a configuration section."""
        return getattr(self.config, section, None)

    def set_section(self, section: str, data: Dict[str, Any]) -> bool:
        """Update a configuration section."""
        try:
            section_class = {
                'acquisition': AcquisitionConfig,
                'recovery': RecoveryConfig,
                'reporting': ReportingConfig,
                'storage': StorageConfig,
                'tools': ToolsConfig,
                'acpo': ACPOConfig,
                'security': SecurityConfig,
            }.get(section)
            
            if section_class is None:
                return False
            
            setattr(self.config, section, section_class(**data))
            return True
        except Exception as e:
            print(f"Error updating configuration section {section}: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.config)

    def to_json(self) -> str:
        """Convert configuration to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_yaml(self) -> str:
        """Convert configuration to YAML."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @staticmethod
    def get_available_profiles() -> List[str]:
        """Get list of available profile names."""
        return [v.value for v in ConfigProfile]

    def list_profiles(self) -> List[Path]:
        """List available profile files."""
        if not self.profiles_dir.exists():
            return []
        return list(self.profiles_dir.glob('*.yaml'))

    def validate_config(self) -> tuple[bool, List[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Validate storage paths are absolute or relative
        storage = self.config.storage
        for path_field in ['base_evidence_dir', 'log_dir', 'temp_dir', 'archive_dir']:
            path_val = Path(getattr(storage, path_field))
            if not path_val.is_absolute():
                # Relative paths are ok, but warn
                pass
        
        # Validate tools exist if ensure_availability is True
        if self.config.tools.ensure_availability:
            from shutil import which
            for tool_field in ['ddrescue_path', 'photorec_path', 'scalpel_path',
                              'fls_path', 'icat_path', 'md5sum_path', 'sha256sum_path']:
                tool_path = getattr(self.config.tools, tool_field)
                if not which(tool_path):
                    errors.append(f"Tool not found: {tool_path}")
        
        # Validate ACPO settings
        acpo = self.config.acpo
        if acpo.case_id_format:
            # Basic validation of case ID format
            if '{year}' not in acpo.case_id_format and '{seq' not in acpo.case_id_format:
                errors.append("Case ID format must include {year} or {seq}")
        
        return len(errors) == 0, errors

    def create_case_paths(self, case_id: str) -> Dict[str, Path]:
        """
        Create and return case directory structure.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Dictionary mapping path names to Path objects
        """
        base_dir = Path(self.config.storage.base_evidence_dir) / case_id
        
        paths = {
            'case': base_dir,
            'images': base_dir / 'images',
            'recovered': base_dir / 'recovered',
            'reports': base_dir / 'reports',
            'temp': base_dir / 'temp',
            'metadata': base_dir / 'metadata',
        }
        
        for path in paths.values():
            path.mkdir(exist_ok=True, parents=True)
        
        return paths


# Module-level configuration instance
_default_config: Optional[ConfigurationManager] = None


def get_config_manager(config_dir: Optional[Path] = None) -> ConfigurationManager:
    """
    Get or create default configuration manager.
    
    Args:
        config_dir: Configuration directory (default: ~/.dfepr/config)
        
    Returns:
        ConfigurationManager instance
    """
    global _default_config
    if _default_config is None:
        _default_config = ConfigurationManager(config_dir)
    return _default_config


if __name__ == '__main__':
    # Example usage
    config_mgr = ConfigurationManager()
    
    # Load production profile
    config_mgr.load_profile('production')
    
    # Display configuration
    print("=" * 60)
    print("DFEPR Configuration Manager")
    print("=" * 60)
    print(f"\nProfile: {config_mgr.config.profile}")
    print(f"Version: {config_mgr.config.version}")
    
    print("\nAcquisition Settings:")
    acq = config_mgr.config.acquisition
    print(f"  Write Block: {acq.write_block}")
    print(f"  Hash Algorithm: {acq.hash_algorithm}")
    print(f"  Chunk Size: {acq.chunk_size_mb}MB")
    
    print("\nStorage Paths:")
    storage = config_mgr.config.storage
    print(f"  Evidence Dir: {storage.base_evidence_dir}")
    print(f"  Log Dir: {storage.log_dir}")
    print(f"  Temp Dir: {storage.temp_dir}")
    
    print("\nTools Configuration:")
    tools = config_mgr.config.tools
    print(f"  ddrescue: {tools.ddrescue_path}")
    print(f"  photorec: {tools.photorec_path}")
    
    print("\nACPO Compliance:")
    acpo = config_mgr.config.acpo
    print(f"  Principle 1 (No modification): {acpo.principle_1_enabled}")
    print(f"  Principle 2 (Chain of Custody): {acpo.principle_2_enabled}")
    print(f"  Principle 3 (Documentation): {acpo.principle_3_enabled}")
    print(f"  Principle 4 (Oversight): {acpo.principle_4_enabled}")
    
    print("\n✓ Configuration management initialized")
    print(f"  Config dir: {config_mgr.config_dir}")
    print(f"  Available profiles: {config_mgr.get_available_profiles()}")
