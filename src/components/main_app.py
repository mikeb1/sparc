import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class MainApp:
    """Main application class for SPARC GUI."""
    
    def __init__(self):
        """Initialize the main application."""
        self.session_state = {}
        self.initialize_session_state()
        self.theme = self.setup_theme()
        self.sidebar = self.create_sidebar()
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
        self.session_state = st.session_state
        
    def setup_theme(self) -> dict:
        """Configure application theme and layout."""
        theme_config = {
            'page_title': "SPARC GUI",
            'layout': "wide",
            'initial_sidebar_state': "expanded"
        }
        st.set_page_config(**theme_config)
        return theme_config
        
    def create_sidebar(self) -> str:
        """Create and configure the sidebar navigation."""
        with st.sidebar:
            st.title("SPARC GUI")
            current_page = st.radio(
                "Navigation",
                ["Project", "Code", "Tests", "Settings"]
            )
        self.current_page = current_page
        return current_page
            
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
        
        # Display appropriate page content
        page_methods = {
            "Project": self._display_project,
            "Code": self._display_code,
            "Tests": self._display_tests,
            "Settings": self._display_settings
        }
        
        if self.current_page in page_methods:
            page_methods[self.current_page]()
            
    def _display_project(self):
        """Display project management interface."""
        st.header("Project Management")
        
    def _display_code(self):
        """Display code editing interface."""
        st.header("Code Editor")
        
    def _display_tests(self):
        """Display test runner interface."""
        st.header("Test Runner")
        
    def _display_settings(self):
        """Display settings interface."""
        st.header("Settings")
