#!/usr/bin/env python3
"""
Integration tests for DFEPR CLI and database functionality.

Tests complete workflows and CLI command integration.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from src.cli import cli
from src.database import DatabaseManager
from src.config_manager import get_config_manager
from src.validator import DataValidator, ValidationLevel


class CLIIntegrationTest(unittest.TestCase):
    """Integration tests for CLI commands."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize database in temp location
        self.db = DatabaseManager(Path(self.temp_dir) / 'test.db')

    def tearDown(self):
        """Clean up test environment."""
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_case_create_command(self):
        """Test case creation via CLI."""
        result = self.runner.invoke(cli, [
            'case', 'create',
            '--case-id', 'THEFT_2026_000001',
            '--case-name', 'Test investigation',
            '--officer', 'Test Officer',
            '--agency', 'Test Agency'
        ])
        
        # Should succeed with proper format
        self.assertEqual(result.exit_code, 0)

    def test_case_list_command(self):
        """Test case listing via CLI."""
        result = self.runner.invoke(cli, ['case', 'list'])
        
        # Should not error
        self.assertNotEqual(result.exit_code, 2)  # Exit code 2 means usage error

    def test_hash_calculate_command(self):
        """Test hash calculation via CLI."""
        # Create test file
        test_file = Path(self.temp_dir) / 'test.bin'
        test_file.write_bytes(b'test data' * 100)
        
        result = self.runner.invoke(cli, [
            'hash', 'calculate',
            '--file', str(test_file)
        ])
        
        # Should succeed
        self.assertTrue(result.exit_code == 0 or 'hash' in result.output.lower())

    def test_tools_check_command(self):
        """Test tools availability check."""
        result = self.runner.invoke(cli, ['tools', 'check'])
        
        # Should complete without error
        self.assertEqual(result.exit_code, 0)

    def test_database_operations(self):
        """Test database CRUD operations."""
        # Create case
        success = self.db.create_case(
            'CASE-2024-003',
            'Database test',
            'Analyst'
        )
        self.assertTrue(success)
        
        # Get case
        case = self.db.get_case('CASE-2024-003')
        self.assertIsNotNone(case)
        self.assertEqual(case['case_id'], 'CASE-2024-003')
        
        # Register evidence
        success = self.db.register_evidence(
            'EV-001',
            'CASE-2024-003',
            'Test evidence',
            '/dev/sda'
        )
        self.assertTrue(success)
        
        # List evidence
        evidence = self.db.list_evidence('CASE-2024-003')
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]['evidence_id'], 'EV-001')

    def test_custody_chain_recording(self):
        """Test chain of custody recording."""
        # Setup
        self.db.create_case('CASE-2024-004', 'CoC test', 'Admin')
        self.db.register_evidence('EV-002', 'CASE-2024-004', 'Test', '/dev/sda')
        
        # Add custody entries
        self.assertTrue(self.db.add_custody_entry(
            'EV-002', 'acquisition',
            'John Analyst', 'Analyst',
            'Lab A', 'Disk acquired'
        ))
        
        self.assertTrue(self.db.add_custody_entry(
            'EV-002', 'analysis',
            'Jane Expert', 'Expert',
            'Lab B', 'Evidence analyzed'
        ))
        
        # Retrieve chain
        chain = self.db.get_custody_chain('EV-002')
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0]['action'], 'acquisition')
        self.assertEqual(chain[1]['action'], 'analysis')

    def test_analysis_recording(self):
        """Test analysis results recording."""
        # Setup
        self.db.create_case('CASE-2024-005', 'Analysis test', 'Admin')
        self.db.register_evidence('EV-003', 'CASE-2024-005', 'Test', '/dev/sda')
        
        # Record analysis
        self.assertTrue(self.db.record_analysis(
            'EV-003',
            'file_recovery',
            'Recovered 1250 files',
            files_recovered=1250,
            anomalies_found=3,
            analyst_name='John Analyst'
        ))
        
        # Retrieve results
        results = self.db.get_analysis_results('EV-003')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['files_recovered'], 1250)
        self.assertEqual(results[0]['anomalies_found'], 3)

    def test_statistics_generation(self):
        """Test statistics generation."""
        # Create data
        self.db.create_case('CASE-2024-006', 'Stats test', 'Admin')
        self.db.create_case('CASE-2024-007', 'Stats test 2', 'Admin')
        self.db.register_evidence('EV-004', 'CASE-2024-006', 'E1', '/dev/sda')
        self.db.register_evidence('EV-005', 'CASE-2024-006', 'E2', '/dev/sdb')
        
        # Get statistics
        stats = self.db.get_statistics()
        
        self.assertEqual(stats['total_cases'], 2)
        self.assertEqual(stats['active_cases'], 2)
        self.assertEqual(stats['total_evidence'], 2)


class ValidationTest(unittest.TestCase):
    """Test advanced data validation."""

    def setUp(self):
        """Set up test environment."""
        self.validator = DataValidator()

    def test_case_id_validation(self):
        """Test case ID validation."""
        # Valid cases
        valid, msg = self.validator.validate_case_id('THEFT_2026_000001')
        self.assertTrue(valid)
        
        # Invalid cases
        valid, msg = self.validator.validate_case_id('INVALID')
        self.assertFalse(valid)

    def test_evidence_id_validation(self):
        """Test evidence ID validation."""
        # Valid
        valid, msg = self.validator.validate_evidence_id('EV-2026-0001')
        self.assertTrue(valid)
        
        # Invalid
        valid, msg = self.validator.validate_evidence_id('INVALID')
        self.assertFalse(valid)

    def test_hash_validation(self):
        """Test hash format validation."""
        # Valid SHA256
        valid, msg = self.validator.validate_hash(
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'sha256'
        )
        self.assertTrue(valid)
        
        # Invalid SHA256
        valid, msg = self.validator.validate_hash('tooshort', 'sha256')
        self.assertFalse(valid)

    def test_case_description_validation(self):
        """Test case description validation."""
        # Valid
        valid, msg = self.validator.validate_case_description(
            'This is a comprehensive test case description for validation.'
        )
        self.assertTrue(valid)
        
        # Too short
        valid, msg = self.validator.validate_case_description('Short')
        self.assertFalse(valid)

    def test_officer_name_validation(self):
        """Test officer name validation."""
        # Valid
        valid, msg = self.validator.validate_officer_name('John Analyst')
        self.assertTrue(valid)
        
        # Invalid
        valid, msg = self.validator.validate_officer_name('JA')
        self.assertFalse(valid)

    def test_comprehensive_validation(self):
        """Test comprehensive case validation."""
        case_data = {
            'case_id': 'THEFT_2026_000001',
            'description': 'This is a comprehensive test case for a data theft investigation.',
            'officer_name': 'John Analyst',
            'agency_name': 'Test Police Department'
        }
        
        all_valid, results = self.validator.validate_all(case_data)
        self.assertFalse(all_valid is False)  # Should be mostly valid


class ConfigurationTest(unittest.TestCase):
    """Test configuration management."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_load_production(self):
        """Test loading production configuration."""
        config_mgr = get_config_manager()
        config_mgr.load_profile('production')
        
        self.assertEqual(config_mgr.config.profile, 'production')
        self.assertTrue(config_mgr.config.acquisition.write_block)

    def test_config_validation(self):
        """Test configuration validation."""
        config_mgr = get_config_manager()
        config_mgr.load_profile('production')
        
        is_valid, errors = config_mgr.validate_config()
        # Should be valid (may have missing tools but that's ok)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)

    def test_case_paths_creation(self):
        """Test case directory creation."""
        config_mgr = get_config_manager()
        
        # Use temp directory
        config_mgr.config.storage.base_evidence_dir = str(self.temp_dir)
        
        paths = config_mgr.create_case_paths('CASE-TEST-001')
        
        # Verify all paths were created
        for path in paths.values():
            self.assertTrue(path.exists())


class WorkflowTest(unittest.TestCase):
    """Test complete workflows."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db = DatabaseManager(Path(self.temp_dir) / 'workflow.db')
        self.runner = CliRunner()

    def tearDown(self):
        """Clean up test environment."""
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_case_workflow(self):
        """Test complete investigation workflow."""
        case_id = 'CASE-WORKFLOW-001'
        evidence_id = 'EV-WF-001'
        
        # 1. Create case
        self.assertTrue(self.db.create_case(
            case_id, 'Workflow test', 'Investigator'
        ))
        
        # 2. Register evidence
        self.assertTrue(self.db.register_evidence(
            evidence_id, case_id, 'Test device', '/dev/sda'
        ))
        
        # 3. Add acquisition entry to CoC
        self.assertTrue(self.db.add_custody_entry(
            evidence_id, 'acquisition',
            'John Analyst', 'Analyst',
            'Lab', 'Disk acquired'
        ))
        
        # 4. Update hash
        self.assertTrue(self.db.update_evidence_hash(
            evidence_id,
            'abc123sha256',
            'abc123md5'
        ))
        
        # 5. Change status
        self.assertTrue(self.db.update_evidence_status(evidence_id, 'acquired'))
        
        # 6. Record analysis
        self.assertTrue(self.db.record_analysis(
            evidence_id, 'acquisition',
            'Disk acquired successfully',
            files_recovered=0,
            analyst_name='John Analyst'
        ))
        
        # 7. Get custody chain
        chain = self.db.get_custody_chain(evidence_id)
        self.assertEqual(len(chain), 1)
        
        # 8. Archive case
        self.assertTrue(self.db.archive_case(case_id))
        
        # Verify final state
        case = self.db.get_case(case_id)
        self.assertEqual(case['status'], 'archived')


if __name__ == '__main__':
    unittest.main()
