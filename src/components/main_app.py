from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

class MainApp:
    """Main application class for SPARC GUI."""
    
    def __init__(self):
        """Initialize the main application."""
        self.app = FastAPI(title="SPARC GUI API")
        self.session_state = {}
        self.initialize_session_state()
        self.setup_routes()
        
    def initialize_session_state(self) -> None:
        """Initialize application state."""
        self.session_state.update({
            'project': None,
            'dark_mode': True,
            'selected_file': None,
            'test_results': None,
            'git_status': None
        })
        
    def setup_routes(self):
        """Set up API routes."""
        @self.app.get("/api/state")
        async def get_state():
            return self.session_state
            
        @self.app.post("/api/state/{key}")
        async def update_state(key: str, value: Any):
            self.session_state[key] = value
            return {"status": "success"}
            
        @self.app.get("/api/project")
        async def get_project():
            return {
                "project": self.session_state.get('project'),
                "files": self._get_project_files()
            }
            
        @self.app.post("/api/project/create")
        async def create_project(name: str):
            self.session_state['project'] = name
            return {"status": "success"}
            
        @self.app.get("/api/git/status")
        async def get_git_status():
            return self.session_state.get('git_status')
            
    def _get_project_files(self) -> list:
        """Get list of project files."""
        if not self.session_state.get('project'):
            return []
        # Implementation would list actual project files
        return ['src/main.py', 'tests/test_main.py']
        
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the application server."""
        uvicorn.run(self.app, host=host, port=port)
            
    def _display_project(self):
        """Display project management interface."""
        st.header("Project Management")
        
        # Add project selection/creation
        if not st.session_state.get('project'):
            st.info("No project selected")
            if st.button("Create New Project"):
                st.session_state.project = "New Project"
        else:
            st.success(f"Current Project: {st.session_state.project}")
            
        # Add project status section
        st.subheader("Project Status")
        st.write("Git Status: Clean")
        
    def _display_code(self):
        """Display code editing interface."""
        st.header("Code Editor")
        
        # Add file browser
        files = ["file1.py", "file2.py"]  # Replace with actual file list
        selected_file = st.selectbox("Select File", files)
        
        if selected_file:
            st.text_area("Edit Code", value="# Code goes here", height=300)
            if st.button("Save Changes"):
                st.success("Changes saved!")

    def _display_tests(self):
        """Display test runner interface."""
        st.header("Test Runner")
        
        # Add test controls
        if st.button("Run All Tests"):
            st.info("Running tests...")
            # Add actual test execution here
            st.success("All tests passed!")
        
        # Add test results section
        st.subheader("Test Results")
        st.write("Last Run: No tests run yet")

    def _display_settings(self):
        """Display settings interface."""
        st.header("Settings")
        
        # Add settings controls
        dark_mode = st.toggle("Dark Mode", value=st.session_state.get('dark_mode', True))
        if dark_mode != st.session_state.get('dark_mode'):
            st.session_state.dark_mode = dark_mode
            st.success("Theme updated!")
        
        # Add other settings
        st.subheader("Git Settings")
        st.text_input("Git Path", value="/usr/bin/git")
        
        if st.button("Save Settings"):
            st.success("Settings saved!")
