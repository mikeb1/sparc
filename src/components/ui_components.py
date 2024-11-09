import streamlit as st
from typing import Tuple, List, Optional

class UIComponents:
    """Reusable UI components for SPARC GUI."""
    
    @staticmethod
    def create_file_browser(files: List[str]) -> Optional[str]:
        """Create a file browser component."""
        if not files:
            st.warning("No files available")
            return None
            
        return st.selectbox(
            "Select File",
            files,
            key="file_browser"
        )
        
    @staticmethod
    def create_progress_bar() -> Tuple[st.progress, st.empty]:
        """Create a progress bar with status message."""
        progress = st.progress(0)
        status = st.empty()
        return progress, status
        
    @staticmethod
    def show_notification(message: str, type: str = "info") -> None:
        """Show a notification message."""
        if type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        elif type == "success":
            st.success(message)
        else:
            st.info(message)
            
    @staticmethod
    def create_modal_dialog(title: str, content: str) -> bool:
        """Create a modal dialog."""
        return st.modal(title, content)
