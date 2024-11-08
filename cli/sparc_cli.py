#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')

    # Architect mode
    parser_architect = subparsers.add_parser('architect', help='Run in architect mode')
    
    args = parser.parse_args()

    if args.mode == 'architect':
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
                with open(file_path, 'w') as f:
                    f.write(f"# {filename[:-3]}\n")
                logger.info(f"Generated {filename}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
