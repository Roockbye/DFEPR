#!/usr/bin/env python3
"""
DFEPR - Basic Test Suite
Tests for core forensic functionality
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime

# Import DFEPR modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.chain_of_custody import ChainOfCustody, CustodyAction, EvidenceRegistry
from src.hash_verifier import HashVerifier
from src.utilities import ValidationHelper, TimestampHelper, SystemHelper, FileHelper


class TestChainOfCustody(unittest.TestCase):
    """Test chain of custody functionality"""
    
    def setUp(self):
        """Setup test case"""
        self.case_id = "TEST_2026_000001"
        self.evidence_id = f"{self.case_id}_001"
        self.temp_dir = tempfile.mkdtemp()
        self.coc = ChainOfCustody(self.case_id, self.temp_dir)
    
    def test_add_entry(self):
        """Test adding custody entry"""
        self.coc.add_entry(
            action=CustodyAction.ACQUISITION,
            person_name="Test User",
            person_title="Examiner",
            location="Lab",
            description="Test acquisition",
            items_affected=["Test Item"]
        )
        
        self.assertEqual(len(self.coc.entries), 1)
        self.assertEqual(self.coc.entries[0].action, "acquisition")
    
    def test_get_history(self):
        """Test retrieving custody history"""
        self.coc.add_entry(
            action=CustodyAction.ACQUISITION,
            person_name="Test User",
            person_title="Examiner",
            location="Lab",
            description="Test",
            items_affected=["Item1"]
        )
        
        history = self.coc.get_history()
        self.assertEqual(len(history), 1)
    
    def test_generate_report(self):
        """Test report generation"""
        self.coc.add_entry(
            action=CustodyAction.ACQUISITION,
            person_name="Test User",
            person_title="Examiner",
            location="Lab",
            description="Test",
            items_affected=["Item1"]
        )
        
        report = self.coc.generate_report()
        self.assertIn("CHAIN OF CUSTODY", report)
        self.assertIn("TEST_2026_000001", report)
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestHashVerifier(unittest.TestCase):
    """Test hash verification functionality"""
    
    def setUp(self):
        """Setup test case"""
        self.case_id = "TEST_2026_000001"
        self.temp_dir = tempfile.mkdtemp()
        self.verifier = HashVerifier(self.case_id, self.temp_dir)
        
        # Create test file
        self.test_file = os.path.join(self.temp_dir, "test.bin")
        with open(self.test_file, 'wb') as f:
            f.write(b"Test data for hashing" * 100)
    
    def test_calculate_hash(self):
        """Test hash calculation"""
        hashes = self.verifier.calculate_hash(
            self.test_file,
            algorithms=["md5", "sha256"]
        )
        
        self.assertIn("md5", hashes)
        self.assertIn("sha256", hashes)
        self.assertEqual(len(hashes["md5"]), 32)  # MD5 is 32 chars
        self.assertEqual(len(hashes["sha256"]), 64)  # SHA256 is 64 chars
    
    def test_register_hash(self):
        """Test hash registration"""
        hashes = self.verifier.register_hash(
            "TEST_001",
            self.test_file,
            description="Test file"
        )
        
        self.assertIn("md5", hashes)
        self.assertIn("TEST_001", self.verifier.hashes)
    
    def test_verify_integrity(self):
        """Test integrity verification"""
        self.verifier.register_hash(
            "TEST_001",
            self.test_file,
            description="Test file"
        )
        
        results = self.verifier.verify_integrity("TEST_001", self.test_file)
        
        self.assertEqual(results["overall_status"], "PASS")
        self.assertTrue(all(
            v["status"] == "PASS" for v in results["verifications"].values()
        ))
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestValidationHelper(unittest.TestCase):
    """Test validation functionality"""
    
    def test_validate_case_id(self):
        """Test case ID validation"""
        # Valid formats
        self.assertTrue(ValidationHelper.validate_case_id("THEFT_2026_000001"))
        self.assertTrue(ValidationHelper.validate_case_id("HOMICIDE_2025_000123"))
        
        # Invalid formats
        self.assertFalse(ValidationHelper.validate_case_id("INVALID"))
        self.assertFalse(ValidationHelper.validate_case_id("THEFT_2026"))
        self.assertFalse(ValidationHelper.validate_case_id("THEFT_XXXX_000001"))
    
    def test_validate_evidence_id(self):
        """Test evidence ID validation"""
        # Valid format
        self.assertTrue(ValidationHelper.validate_evidence_id("THEFT_2026_000001_001"))
        
        # Invalid format
        self.assertFalse(ValidationHelper.validate_evidence_id("INVALID"))
    
    def test_validate_hash(self):
        """Test hash validation"""
        # Valid MD5
        valid_md5 = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        # Note: This is NOT actually valid MD5 (contains g, h, k, l, n, o, p which are invalid hex)
        # Valid MD5 would be all 0-9 and a-f
        
        # Actually valid MD5
        valid_md5 = "5d41402abc4b2a76b9719d911017c592"
        self.assertTrue(ValidationHelper.validate_hash(valid_md5, "md5"))
        
        # Actually valid SHA256
        valid_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertTrue(ValidationHelper.validate_hash(valid_sha256, "sha256"))
    
    def test_invalid_hash(self):
        """Test invalid hash"""
        # Too short
        self.assertFalse(ValidationHelper.validate_hash("abc", "md5"))
        
        # Invalid characters
        self.assertFalse(ValidationHelper.validate_hash("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", "md5"))


class TestTimestampHelper(unittest.TestCase):
    """Test timestamp functionality"""
    
    def test_get_utc_timestamp(self):
        """Test UTC timestamp generation"""
        ts = TimestampHelper.get_utc_timestamp()
        
        # Should end with Z
        self.assertTrue(ts.endswith("Z"))
        
        # Should be ISO format
        self.assertIn("T", ts)
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        ts = "2026-04-03T10:15:30Z"
        formatted = TimestampHelper.format_timestamp(ts)
        
        self.assertIn("2026", formatted)
        self.assertIn("04-03", formatted)
    
    def test_readable_timestamp(self):
        """Test readable timestamp"""
        ts = TimestampHelper.get_readable_timestamp()
        
        # Should contain date components
        self.assertIn("-", ts)
        self.assertIn(":", ts)
        self.assertIn("UTC", ts)


class TestSystemHelper(unittest.TestCase):
    """Test system functionality"""
    
    def test_check_tool_available(self):
        """Test tool availability check"""
        # ls should be available on all systems
        self.assertTrue(SystemHelper.check_tool_available("ls"))
        
        # nonexistent_tool_xyz should not be available
        self.assertFalse(SystemHelper.check_tool_available("nonexistent_tool_xyz_12345"))
    
    def test_format_bytes(self):
        """Test byte formatting"""
        self.assertEqual(SystemHelper.format_bytes(1024), "1.00 KB")
        self.assertEqual(SystemHelper.format_bytes(1048576), "1.00 MB")
        
        # Test small bytes
        formatted = SystemHelper.format_bytes(512)
        self.assertIn("B", formatted)


class TestEvidenceRegistry(unittest.TestCase):
    """Test evidence registry"""
    
    def setUp(self):
        """Setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = EvidenceRegistry(self.temp_dir)
    
    def test_register_evidence(self):
        """Test registering evidence"""
        result = self.registry.register_evidence(
            evidence_id="TEST_001",
            case_id="TEST_CASE",
            description="Test evidence",
            source="/dev/sda",
            hash_md5="abc123",
            hash_sha256="def456"
        )
        
        self.assertTrue(result)
        self.assertIn("TEST_001", self.registry.evidence)
    
    def test_get_case_evidence(self):
        """Test getting evidence for case"""
        self.registry.register_evidence(
            evidence_id="TEST_001",
            case_id="CASE_A",
            description="Item 1",
            source="/dev/sda",
            hash_md5="abc",
            hash_sha256="def"
        )
        
        self.registry.register_evidence(
            evidence_id="TEST_002",
            case_id="CASE_A",
            description="Item 2",
            source="/dev/sdb",
            hash_md5="ghi",
            hash_sha256="jkl"
        )
        
        case_evidence = self.registry.get_case_evidence("CASE_A")
        self.assertEqual(len(case_evidence), 2)
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestChainOfCustody))
    suite.addTests(loader.loadTestsFromTestCase(TestHashVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationHelper))
    suite.addTests(loader.loadTestsFromTestCase(TestTimestampHelper))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemHelper))
    suite.addTests(loader.loadTestsFromTestCase(TestEvidenceRegistry))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
