from pathlib import Path
import toml
import git
from typing import Dict, Optional, List
import streamlit as st
from datetime import datetime
import glob

def scan_architecture_folders(base_path: str) -> List[Dict]:
    """Scan for architecture_* folders and extract project info."""
    arch_folders = []
    pattern = f"{base_path}/architecture_*"
    
    for folder in glob.glob(pattern):
        folder_path = Path(folder)
        if folder_path.is_dir():
            # Try to load guidance.toml
            guidance_file = folder_path / "guidance.toml"
            guidance = {}
            if guidance_file.exists():
                try:
                    with open(guidance_file) as f:
                        guidance = toml.load(f)
                except Exception:
                    pass
                    
            # Get folder creation time
            try:
                created = datetime.fromtimestamp(folder_path.stat().st_ctime)
            except:
                created = datetime.now()
                
            arch_folders.append({
                "path": str(folder_path),
                "name": folder_path.name,
                "created": created,
                "guidance": guidance
            })
            
    return sorted(arch_folders, key=lambda x: x["created"], reverse=True)

def load_project_files(project_path: str) -> Dict:
    """Load all relevant project files and return their contents."""
    path = Path(project_path)
    files = {}
    
    # Load architecture files
    arch_files = path.glob("*.md")
    for file in arch_files:
        try:
            files[file.name] = file.read_text()
        except Exception as e:
            st.warning(f"Could not read {file.name}: {str(e)}")
            
    # Load guidance.toml
    guidance_file = path / "guidance.toml"
    if guidance_file.exists():
        try:
            with open(guidance_file) as f:
                files["guidance.toml"] = toml.load(f)
        except Exception as e:
            st.warning(f"Could not read guidance.toml: {str(e)}")
            
    return files

def init_git_repo(path: str) -> Optional[git.Repo]:
    """Initialize or load git repository."""
    try:
        repo = git.Repo(path)
        return repo
    except git.InvalidGitRepositoryError:
        try:
            return git.Repo.init(path)
        except Exception as e:
            st.error(f"Failed to initialize git repository: {str(e)}")
            return None
