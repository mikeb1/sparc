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
        self.setup_theme()
        self.create_sidebar()
        
    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state."""
        if 'project' not in st.session_state:
            st.session_state['project'] = None
        if 'dark_mode' not in st.session_state:
            st.session_state['dark_mode'] = True
        
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
            st.image("logo.png")
            st.title("SPARC GUI")
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
        st.title(f"SPARC GUI - {self.current_page}")
        
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
        
    def _display_code(self):
        """Display code editing interface."""
        st.header("Code Editor")
        
    def _display_tests(self):
        """Display test runner interface."""
        st.header("Test Runner")
        
    def _display_settings(self):
        """Display settings interface."""
        st.header("Settings")
