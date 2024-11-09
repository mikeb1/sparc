import os
from git import Repo

class ProjectManager:
    def __init__(self):
        self.current_project = None

    def initialize_project(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        if self.config.use_git:
            repo = Repo.init(path)
            self.repo = repo
        self.current_project = path

    def load_project(self, path: str):
        if os.path.exists(path):
            self.current_project = path
            os.chdir(path)
            # Load additional configurations if necessary
        else:
            raise FileNotFoundError(f"Project at {path} does not exist.")

    def save_project(self):
        if self.repo and self.config.auto_commits:
            self.repo.git.add('--all')
            self.repo.index.commit('Auto-commit changes')
