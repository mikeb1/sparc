from unittest.mock import Mock, patch
import os
from pathlib import Path
from code_analyzer import CodeAnalyzer

def test_code_analyzer_scans_repository():
    """Test that CodeAnalyzer can scan a repository and analyze patterns"""
    # Arrange
    mock_fs = Mock()
    mock_git = Mock()
    mock_fs.glob.return_value = [Path("test.py")]
    mock_fs.read_text.return_value = "print('hello')"
    
    analyzer = CodeAnalyzer(mock_fs, mock_git)
    
    # Act
    results = analyzer.analyze_repository("/fake/repo")
    
    # Assert
    assert results["files_analyzed"] == 1
    mock_fs.glob.assert_called_with("**/*.py")
    mock_fs.read_text.assert_called()
    mock_git.get_file_history.assert_called()

def test_code_analyzer_identifies_security_patterns():
    """Test that CodeAnalyzer can identify security issues"""
    # Arrange
    mock_fs = Mock()
    mock_git = Mock()
    mock_fs.glob.return_value = [Path("test.py")]
    mock_fs.read_text.return_value = """
    def unsafe_query(user_input):
        query = f"SELECT * FROM users WHERE id = {user_input}"
    """
    
    analyzer = CodeAnalyzer(mock_fs, mock_git)
    
    # Act
    results = analyzer.analyze_security("/fake/repo")
    
    # Assert
    assert len(results["security_issues"]) == 1
    issue = results["security_issues"][0]
    assert issue.type == "SQL_INJECTION"
    assert issue.file == "test.py"
    assert issue.line_number == 3
