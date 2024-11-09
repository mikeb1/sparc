import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the root directory of the repository."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def output_dir(repo_root):
    """Create and manage the permanent test outputs directory."""
    output_dir = repo_root / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Clear existing test outputs except .gitkeep
    for item in output_dir.iterdir():
        if item.name != '.gitkeep':
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
                
    return output_dir

@pytest.fixture(scope="session")
def cli_script(repo_root):
    """Return path to the CLI script."""
    return repo_root / "cli" / "sparc_cli.py"

@pytest.fixture
def clean_test_dir(tmp_path):
    """Create a clean test directory for each test."""
    yield tmp_path
    # Cleanup after test
    shutil.rmtree(tmp_path)
import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the root directory of the repository."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def cli_script(repo_root):
    """Return path to the CLI script."""
    return repo_root / "cli" / "sparc_cli.py"

@pytest.fixture
def clean_test_dir(tmp_path):
    """Create a clean test directory for each test."""
    yield tmp_path
    # Cleanup after test
    shutil.rmtree(tmp_path)
"""Shared pytest fixtures for SPARC GUI tests."""

import pytest
from unittest.mock import MagicMock
import streamlit as st

@pytest.fixture
def mock_streamlit():
    """Mock streamlit functionality for testing."""
    # Store original streamlit functions
    original_sidebar = getattr(st, 'sidebar', None)
    original_title = getattr(st, 'title', None)
    original_image = getattr(st, 'image', None)
    original_radio = getattr(st, 'radio', None)
    
    # Create mock functions
    st.sidebar = MagicMock()
    st.title = MagicMock()
    st.image = MagicMock()
    st.radio = MagicMock()
    
    yield st
    
    # Restore original functions
    st.sidebar = original_sidebar
    st.title = original_title
    st.image = original_image
    st.radio = original_radio

@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state."""
    original_session_state = getattr(st, 'session_state', {})
    st.session_state = {}
    
    yield st.session_state
    
    st.session_state = original_session_state

@pytest.fixture
def mock_git():
    """Mock Git functionality."""
    git_mock = MagicMock()
    git_mock.status = MagicMock(return_value=MagicMock(
        untracked_files=[],
        modified=[],
        staged=[]
    ))
    return git_mock

@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    fs_mock = MagicMock()
    fs_mock.exists = MagicMock(return_value=True)
    fs_mock.read_text = MagicMock(return_value="Test content")
    fs_mock.write_text = MagicMock()
    return fs_mock
