"""Settings manager component for SPARC GUI."""

import streamlit as st
from typing import Dict, Any, Optional
import toml
from pathlib import Path

class SettingsManager:
    """Manages application settings and configuration."""
    
    def __init__(self):
        """Initialize settings manager."""
        self.settings = {
            'dark_mode': True,
            'git_path': '/usr/bin/git'
        }
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from configuration file."""
        config_path = Path.home() / '.sparc' / 'config.toml'
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.settings.update(toml.load(f))
        except Exception as e:
            st.error(f"Failed to load settings: {str(e)}")
        return self.settings
        
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to configuration file."""
        config_path = Path.home() / '.sparc' / 'config.toml'
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                toml.dump(settings, f)
            self.settings.update(settings)
            return True
        except Exception as e:
            st.error(f"Failed to save settings: {str(e)}")
            return False
            
    def update_setting(self, key: str, value: Any) -> None:
        """Update a single setting."""
        if key not in self.settings:
            raise ValueError(f"Invalid setting key: {key}")
        self.settings[key] = value
