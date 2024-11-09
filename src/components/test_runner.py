"""Test runner component for SPARC GUI."""

import streamlit as st
from typing import Dict, List, Optional
import pytest
from pathlib import Path

class TestRunner:
    """Manages test discovery and execution."""
    
    def __init__(self):
        """Initialize test runner."""
        self.test_suite = None
        self.coverage = None
        self.test_results = None
        
    def discover_tests(self) -> List[str]:
        """Discover available tests."""
        test_dir = Path("tests")
        if not test_dir.exists():
            return []
            
        test_files = []
        for path in test_dir.glob("**/*test*.py"):
            test_files.append(str(path))
        return test_files
        
    def run_tests(self, test_files: Optional[List[str]] = None) -> Dict:
        """Run the test suite."""
        args = ["-v"]
        if test_files:
            args.extend(test_files)
            
        exit_code = pytest.main(args)
        
        return {
            'status': 'passed' if exit_code == 0 else 'failed',
            'exit_code': exit_code
        }
        
    def generate_report(self) -> Dict:
        """Generate test execution report."""
        if not self.test_results:
            return {'error': 'No test results available'}
            
        return {
            'passed': self.test_results.get('passed', 0),
            'failed': self.test_results.get('failed', 0),
            'coverage': self.coverage
        }
