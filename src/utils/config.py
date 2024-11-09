"""Configuration management utilities for SPARC GUI."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import toml

class Config:
    """Configuration management class."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_file = config_file or self._get_default_config_file()
        self.config = self.load_config()
        
    def _get_default_config_file(self) -> str:
        """Get the default configuration file path."""
        # Check common locations
        locations = [
            Path.cwd() / '.sparc.toml',
            Path.home() / '.sparc' / 'config.toml'
        ]
        
        for loc in locations:
            if loc.exists():
                return str(loc)
                
        # Return default location
        default = Path.home() / '.sparc' / 'config.toml'
        default.parent.mkdir(parents=True, exist_ok=True)
        return str(default)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    return toml.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            
        # Return default config if loading fails
        return self.get_default_config()
        
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                toml.dump(self.config, f)
            return True
            
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
            
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        return {
            'app': {
                'name': 'SPARC GUI',
                'version': '0.1.0',
                'dark_mode': True
            },
            'paths': {
                'git': '/usr/bin/git',
                'projects': str(Path.home() / 'sparc_projects')
            },
            'editor': {
                'theme': 'dark',
                'font_size': 12,
                'tab_size': 4
            },
            'git': {
                'auto_commit': True,
                'commit_message_prefix': 'sparc: '
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            # Support nested keys with dot notation
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        try:
            # Support nested keys with dot notation
            keys = key.split('.')
            config = self.config
            
            # Navigate to the correct nested level
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            # Set the value
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"Error setting config value: {str(e)}")
            return False
