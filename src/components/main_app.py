import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class MainApp:
    """Main application class for SPARC GUI."""
    
    def __init__(self):
        """Initialize the main application."""
        self.session_state = self.initialize_session_state()
        self.theme = self.setup_theme()
        self.sidebar = self.create_sidebar()
        
    def initialize_session_state(self) -> Dict:
        """Initialize Streamlit session state."""
        state = st.session_state
        if not hasattr(state, 'project'):
            state['project'] = None
        if not hasattr(state, 'dark_mode'):
            state['dark_mode'] = True
        return state
        
    def setup_theme(self):
        """Configure application theme and layout."""
        st.set_page_config(
            layout="wide",
            initial_sidebar_state="expanded"
        )
        return self._apply_custom_css()
        
    def create_sidebar(self):
        """Create and configure the sidebar navigation."""
        with st.sidebar:
            st.image("logo.png")
            st.title("SPARC GUI")
            return st.radio(
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
        st.title(f"SPARC GUI - {self.sidebar}")
        
        if self.sidebar == "Project":
            self._display_project()
        elif self.sidebar == "Code":
            self._display_code()
        elif self.sidebar == "Tests":
            self._display_tests()
        elif self.sidebar == "Settings":
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
