from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    type: str
    file: str
    line_number: int
    description: str

class CodeAnalyzer:
    """Analyzes code repositories for patterns and security issues"""
    
    def __init__(self, file_system, git_client):
        self.file_system = file_system
        self.git_client = git_client

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze a repository for code patterns"""
        python_files = list(self.file_system.glob("**/*.py"))
        
        # Read and analyze each file
        analysis_results = {
            "files_analyzed": len(python_files),
            "patterns_found": []
        }
        
        for file_path in python_files:
            content = self.file_system.read_text(file_path)
            # Get git history for the file
            self.git_client.get_file_history(file_path)
            
            # Analyze patterns in the file
            patterns = self._analyze_file_patterns(content)
            if patterns:
                analysis_results["patterns_found"].extend(patterns)
        
        return analysis_results

    def analyze_security(self, repo_path: str) -> Dict[str, List[SecurityIssue]]:
        """Analyze a repository for security issues"""
        python_files = list(self.file_system.glob("**/*.py"))
        security_issues = []
        
        for file_path in python_files:
            content = self.file_system.read_text(file_path)
            issues = self._find_security_issues(content, str(file_path))
            security_issues.extend(issues)
        
        return {"security_issues": security_issues}

    def _analyze_file_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Analyze patterns in a single file"""
        patterns = []
        # Add pattern analysis logic here
        return patterns

    def _find_security_issues(self, content: str, filename: str) -> List[SecurityIssue]:
        """Find security issues in a single file"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for SQL injection vulnerabilities
            if 'SELECT' in line and '{' in line:
                issues.append(SecurityIssue(
                    type="SQL_INJECTION",
                    file=filename,
                    line_number=i,
                    description="Potential SQL injection vulnerability detected"
                ))
                
        return issues
