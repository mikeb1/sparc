#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

from dataclasses import dataclass
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SPARCConfig:
    """Configuration class for SPARC CLI."""
    # Core directories
    architecture_dir: str = "architecture"
    test_dir: str = "tests" 
    source_dir: str = "src"
    
    # Development settings
    max_attempts: int = 3
    verbose: bool = False
    guidance_file: str = "guidance.toml"
    
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
    
    # Aider settings
    aider_model: str = "claude-3-sonnet-20240229"  # Default to Claude 3.5 Sonnet
    aider_edit_format: str = "diff"
    aider_stream: bool = True
    aider_auto_commits: bool = True

def main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')

    # Common arguments for all modes
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--model', type=str,
                             choices=['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'gpt-4', 'gpt-4-turbo'],
                             default='claude-3-sonnet-20240229',
                             help='AI model to use (default: claude-3-sonnet-20240229)')

    # Architect mode
    parser_architect = subparsers.add_parser('architect', parents=[parent_parser], help='Run in architect mode')
    parser_architect.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')

    # Implement mode
    parser_implement = subparsers.add_parser('implement', parents=[parent_parser], help='Run in implementation mode')
    parser_implement.add_argument('--max-attempts', type=int, default=3,
                                help='Maximum attempts for implementation')
    parser_implement.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')

    args = parser.parse_args()
    
    # Update config with selected model
    config = SPARCConfig(
        aider_model=args.model if hasattr(args, 'model') else 'claude-3-sonnet-20240229'
    )

    if args.mode == 'architect':
        try:
            import toml
            if os.path.exists(args.guidance_file):
                with open(args.guidance_file, 'r') as f:
                    guidance = toml.load(f)
            else:
                guidance = {}
        except Exception as e:
            logger.warning(f"Failed to load guidance file: {e}")
            guidance = {}
        # Create architecture directory
        arch_dir = Path("architecture")
        arch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created architecture directory")

        # Create empty architecture files
        files_to_generate = [
            "Specification.md",
            "Pseudocode.md", 
            "Architecture.md",
            "Refinement.md",
            "Completion.md"
        ]

        for filename in files_to_generate:
            file_path = arch_dir / filename
            if not file_path.exists():
                content = guidance.get(filename[:-3].lower(), {}).get('content', f"# {filename[:-3]}\n")
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Generated {filename}")
    elif args.mode == 'implement':
        # Read Architecture.md to find components
        arch_file = Path("architecture/Architecture.md")
        if not arch_file.exists():
            logger.error("Architecture.md not found. Run architect mode first.")
            sys.exit(1)

        with open(arch_file, 'r') as f:
            content = f.read()

        # Parse components
        import re
        components = re.findall(r'## Component: (\w+)', content)
        if not components:
            logger.error("No components found in Architecture.md")
            sys.exit(1)

        # Create source and test directories
        src_dir = Path("src")
        test_dir = Path("tests")
        src_dir.mkdir(exist_ok=True)
        test_dir.mkdir(exist_ok=True)

        # Generate files for each component
        for component in components:
            component_lower = component.lower()
            src_file = src_dir / f"{component_lower}.py"
            test_file = test_dir / f"test_{component_lower}.py"

            if not src_file.exists():
                with open(src_file, 'w') as f:
                    f.write(f"class {component}:\n    pass\n")
                logger.info(f"Generated {src_file}")

            if not test_file.exists():
                with open(test_file, 'w') as f:
                    f.write(f"def test_{component_lower}():\n    pass\n")
                logger.info(f"Generated {test_file}")

        logger.info("Implementation completed successfully")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
