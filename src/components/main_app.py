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
        if 'project' not in st.session_state:
            st.session_state.project = None
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = True
        return st.session_state
        
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
