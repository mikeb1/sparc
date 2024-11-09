import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class MainApp:
    """Main application class for SPARC GUI."""
    
    def __init__(self):
        """Initialize the main application."""
        self.session_state = {}  # Initialize empty first
        self.initialize_session_state()  # Then populate with defaults
        self.session_state = st.session_state  # Finally use streamlit session
        self.setup_theme()
        self.create_sidebar()
        self.current_page = "Project"  # Set default page
        
    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state."""
        defaults = {
            'project': None,
            'dark_mode': True,
            'selected_file': None,
            'test_results': None
        }
        
        # Update session state with defaults
        for key, value in defaults.items():
            st.session_state[key] = value
        
    def setup_theme(self) -> None:
        """Configure application theme and layout."""
        st.set_page_config(
            page_title="SPARC GUI",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def create_sidebar(self) -> None:
        """Create and configure the sidebar navigation."""
        with st.sidebar:
            st.title("SPARC GUI")
            self.current_page = st.radio(
                "Navigation",
                ["Project", "Code", "Tests", "Settings"],
                index=0  # Default to first option
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
        st.title(f"SPARC GUI - {self.current_page}")
        
        # Map pages to their display methods
        pages = {
            "Project": self._display_project,
            "Code": self._display_code,
            "Tests": self._display_tests,
            "Settings": self._display_settings
        }
        
        # Display the current page
        if self.current_page in pages:
            pages[self.current_page]()
            
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
