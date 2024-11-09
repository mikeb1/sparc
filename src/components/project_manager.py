from pathlib import Path
from typing import Optional, List, Dict
import streamlit as st
import git

class ProjectManager:
    """Manages project operations and Git integration."""
    
    def __init__(self):
        """Initialize the project manager."""
        self.current_project: Optional[Path] = None
        self.git_repo = None
        
    def initialize_project(self, path: str) -> bool:
        """Initialize a new project at the given path."""
        project_path = Path(path)
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize git repo
            if not (project_path / '.git').exists():
                git.Repo.init(project_path)
            
            self.current_project = project_path
            self.git_repo = git.Repo(project_path)
            
            # Create standard directories
            (project_path / 'src').mkdir(exist_ok=True)
            (project_path / 'tests').mkdir(exist_ok=True)
            (project_path / 'docs').mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize project: {str(e)}")
            return False
            
    def get_project_files(self) -> List[Path]:
        """Get list of files in current project."""
        if not self.current_project:
            return []
            
        files = []
        for ext in ['.py', '.md', '.txt']:
            files.extend(self.current_project.glob(f'**/*{ext}'))
        return files
        
    def get_git_status(self) -> Dict[str, List[str]]:
        """Get Git repository status."""
        if not self.git_repo:
            return {'error': ['No Git repository initialized']}
            
        try:
            status = self.git_repo.git.status()
            return {
                'modified': self.git_repo.index.diff(None),
                'untracked': self.git_repo.untracked_files,
                'staged': self.git_repo.index.diff('HEAD')
            }
        except Exception as e:
            return {'error': [str(e)]}
