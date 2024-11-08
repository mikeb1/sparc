import pytest
from dataclasses import dataclass
from typing import Optional
from cli.sparc_cli import SPARCConfig

def test_default_config():
    """Test default configuration values."""
    config = SPARCConfig()
    assert config.architecture_dir == "architecture"
    assert config.test_dir == "tests"
    assert config.source_dir == "src"
    assert config.max_attempts == 3
    assert config.verbose is False
    assert config.guidance_file == "guidance.toml"
    assert config.use_git is True
    assert config.auto_commits is True
    assert config.dirty_commits is True
    assert config.auto_test is False
    assert config.test_cmd is None
    assert config.pretty is True
    assert config.stream is True

def test_custom_config():
    """Test custom configuration values."""
    config = SPARCConfig(
        architecture_dir="custom_arch",
        max_attempts=5,
        verbose=True,
        use_git=False,
        auto_commits=False
    )
    assert config.architecture_dir == "custom_arch"
    assert config.max_attempts == 5
    assert config.verbose is True
    assert config.use_git is False
    assert config.auto_commits is False
