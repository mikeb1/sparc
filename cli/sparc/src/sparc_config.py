from dataclasses import dataclass
from typing import Optional

@dataclass
class SPARCConfig:
    # Core directories
    architecture_dir: str = "architecture"
    test_dir: str = "tests"
    source_dir: str = "src"

    # Development settings
    max_attempts: int = 3
    verbose: bool = False
    guidance_file: str = "guidance.toml"

    # Model settings
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4000
    litellm_api_key: Optional[str] = None

    # Git settings
    use_git: bool = True
    auto_commits: bool = True
    dirty_commits: bool = True

    # Testing settings
    auto_test: bool = False
    test_cmd: Optional[str] = None

    # Output settings
    pretty: bool = True
    stream: bool = True
