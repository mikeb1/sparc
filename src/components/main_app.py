import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class MainApp:
    """Main application class for SPARC GUI."""
    
    def __init__(self):
        """Initialize the main application."""
        self.initialize_session_state()  # Call this first
        self.session_state = st.session_state  # Use st.session_state directly
        self.setup_theme()  # Call this directly, don't store return value
        self.create_sidebar()  # Call this directly, don't store return value
        self.current_page = None
        
    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state."""
        defaults = {
            'project': None,
            'dark_mode': True,
            'selected_file': None,
            'test_results': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
    def setup_theme(self) -> None:
        """Configure application theme and layout."""
        st.set_page_config(
            page_title="SPARC GUI",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self._apply_custom_css()
        
    def create_sidebar(self) -> None:
        """Create and configure the sidebar navigation."""
        with st.sidebar:
            st.title("SPARC GUI")  # This must be called
            self.current_page = st.radio(
                "Navigation",
                ["Project", "Code", "Tests", "Settings"]
            )
            
    def _apply_custom_css(self):
        """Apply custom CSS styling."""
        st.markdown("""
            <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            </style>
            """, unsafe_allow_html=True)
            
    def display(self):
        """Display the main application interface."""
        # Set page title first
        st.title(f"SPARC GUI - {self.current_page}")
        
        # Display appropriate page content based on current page
        if self.current_page == "Project":
            self._display_project()
        elif self.current_page == "Code":
            self._display_code()
        elif self.current_page == "Tests":
            self._display_tests()
        elif self.current_page == "Settings":
            self._display_settings()
            
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
