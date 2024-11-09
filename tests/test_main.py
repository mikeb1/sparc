"""Integration tests for the SPARC GUI main application."""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

def test_main_app_initialization(mock_streamlit, mock_session_state):
    """Test that the main app initializes correctly."""
    from src.main import main
    
    # Run main app
    main()
    
    # Verify streamlit setup
    mock_streamlit.set_page_config.assert_called_once()
    mock_streamlit.sidebar.assert_called_once()
    
    # Verify session state initialization
    assert 'project' in mock_session_state
    assert 'dark_mode' in mock_session_state

def test_navigation_flow(mock_streamlit):
    """Test navigation between different sections."""
    from src.main import main
    
    # Mock navigation selection
    mock_streamlit.sidebar.radio.return_value = "Project"
    
    # Run main app
    main()
    
    # Verify navigation setup
    mock_streamlit.sidebar.radio.assert_called_with(
        "Navigation",
        ["Project", "Code", "Tests", "Settings"]
    )

@pytest.mark.parametrize("page", ["Project", "Code", "Tests", "Settings"])
def test_page_rendering(mock_streamlit, page):
    """Test that each page renders correctly."""
    from src.main import main
    
    # Mock page selection
    mock_streamlit.sidebar.radio.return_value = page
    
    # Run main app
    main()
    
    # Verify page title is set
    mock_streamlit.title.assert_called_once()

def test_dark_mode_initialization(mock_streamlit, mock_session_state):
    """Test dark mode is initialized correctly."""
    from src.main import main
    
    # Run main app
    main()
    
    # Verify dark mode is set in session state
    assert mock_session_state.get('dark_mode') is True
