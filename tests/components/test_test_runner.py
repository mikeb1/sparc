"""Unit tests for the TestRunner component using London-style TDD."""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

def test_test_runner_initialization(mock_streamlit):
    """Test TestRunner component initialization."""
    from src.components.test_runner import TestRunner
    
    # Create TestRunner instance
    runner = TestRunner()
    
    # Verify initialization
    assert runner.test_suite is None
    assert runner.coverage is None

def test_discover_tests(mock_streamlit):
    """Test test discovery functionality."""
    from src.components.test_runner import TestRunner
    
    # Mock test files
    test_files = ["test_1.py", "test_2.py"]
    
    with patch('pathlib.Path.glob') as mock_glob:
        mock_glob.return_value = test_files
        
        runner = TestRunner()
        discovered = runner.discover_tests()
        
        assert len(discovered) == len(test_files)
        mock_glob.assert_called_once()

def test_run_tests(mock_streamlit):
    """Test test execution functionality."""
    from src.components.test_runner import TestRunner
    
    # Mock test execution
    with patch('pytest.main') as mock_pytest:
        mock_pytest.return_value = 0  # Success
        
        runner = TestRunner()
        result = runner.run_tests()
        
        assert result['status'] == 'passed'
        mock_pytest.assert_called_once()

def test_generate_report(mock_streamlit):
    """Test test report generation."""
    from src.components.test_runner import TestRunner
    
    runner = TestRunner()
    
    # Mock test results
    runner.test_results = {
        'passed': 5,
        'failed': 0,
        'coverage': 85.5
    }
    
    report = runner.generate_report()
    
    assert 'passed' in report
    assert 'coverage' in report
