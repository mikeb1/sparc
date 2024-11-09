"""Unit tests for the SettingsManager component using London-style TDD."""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

def test_settings_manager_initialization(mock_streamlit):
    """Test SettingsManager component initialization."""
    from src.components.settings_manager import SettingsManager
    
    # Create SettingsManager instance
    manager = SettingsManager()
    
    # Verify default settings
    assert hasattr(manager, 'settings')
    assert 'dark_mode' in manager.settings
    assert 'git_path' in manager.settings

def test_load_settings(mock_streamlit, mock_file_system):
    """Test settings loading functionality."""
    from src.components.settings_manager import SettingsManager
    
    # Mock settings file content
    mock_settings = {
        'dark_mode': True,
        'git_path': '/usr/bin/git'
    }
    
    with patch('toml.load') as mock_toml:
        mock_toml.return_value = mock_settings
        
        manager = SettingsManager()
        loaded_settings = manager.load_settings()
        
        assert loaded_settings == mock_settings
        mock_toml.assert_called_once()

def test_save_settings(mock_streamlit, mock_file_system):
    """Test settings saving functionality."""
    from src.components.settings_manager import SettingsManager
    
    # Test settings to save
    test_settings = {
        'dark_mode': False,
        'git_path': '/custom/git'
    }
    
    with patch('toml.dump') as mock_toml:
        manager = SettingsManager()
        manager.save_settings(test_settings)
        
        mock_toml.assert_called_once()
        args = mock_toml.call_args[0]
        assert args[0] == test_settings

def test_update_setting(mock_streamlit):
    """Test individual setting update."""
    from src.components.settings_manager import SettingsManager
    
    manager = SettingsManager()
    
    # Update a setting
    manager.update_setting('dark_mode', False)
    assert manager.settings['dark_mode'] is False
    
    # Test invalid setting
    with pytest.raises(ValueError):
        manager.update_setting('invalid_setting', 'value')
