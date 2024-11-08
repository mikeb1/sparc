import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_component_detection(clean_test_dir, cli_script):
    """Test that components are correctly detected from Architecture.md."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create architecture directory and Architecture.md with multiple components
    arch_dir = clean_test_dir / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)

    architecture_content = """# Architecture

## Component: DataValidator
Validates input data formats.

## Component: DataTransformer
Transforms data between formats.

## Component: DataExporter
Exports data to various formats.
"""
    
    with open(arch_dir / "Architecture.md", "w") as f:
        f.write(architecture_content)

    # Run implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that all expected component files were created
    expected_files = [
        ("src/datavalidator.py", "DataValidator"),
        ("src/datatransformer.py", "DataTransformer"),
        ("src/dataexporter.py", "DataExporter"),
        ("tests/test_datavalidator.py", "DataValidator"),
        ("tests/test_datatransformer.py", "DataTransformer"),
        ("tests/test_dataexporter.py", "DataExporter")
    ]

    for filepath, component_name in expected_files:
        full_path = clean_test_dir / filepath
        assert full_path.exists(), f"Expected file {filepath} for component {component_name} was not created"
        assert full_path.stat().st_size > 0, f"File {filepath} for component {component_name} is empty"

    print("Test 4 passed: Component detection works correctly")
