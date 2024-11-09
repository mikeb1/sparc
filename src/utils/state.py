"""State management utilities for SPARC GUI."""

from typing import Dict, Any, Optional
import streamlit as st

class State:
    """State management class using Streamlit session state."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize default state values."""
        defaults = {
            'project': None,
            'dark_mode': True,
            'selected_file': None,
            'test_results': None,
            'git_status': None,
            'notifications': []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return st.session_state.get(key, default)
        
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set a value in the state."""
        st.session_state[key] = value
        
    @staticmethod
    def delete(key: str) -> None:
        """Delete a value from the state."""
        if key in st.session_state:
            del st.session_state[key]
            
    @staticmethod
    def clear() -> None:
        """Clear all state values."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        State.initialize()
        
    @staticmethod
    def add_notification(message: str, type: str = 'info') -> None:
        """Add a notification to the state."""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
            
        st.session_state.notifications.append({
            'message': message,
            'type': type
        })
        
    @staticmethod
    def get_notifications() -> list:
        """Get all notifications."""
        return st.session_state.get('notifications', [])
        
    @staticmethod
    def clear_notifications() -> None:
        """Clear all notifications."""
        st.session_state.notifications = []
