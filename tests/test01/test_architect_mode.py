import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_architect_mode_generates_files(clean_test_dir, cli_script):
    """Test that architect mode generates all expected architecture files."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Run the architect mode
    cmd = ["python", "sparc_cli.py", "architect"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result.returncode == 0, f"Architect mode failed: {result.stderr}"

    # Check that the architecture directory was created
    arch_dir = clean_test_dir / "architecture"
    assert arch_dir.exists(), "Architecture directory was not created."

    # Check that all expected files are present
    expected_files = [
        "Specification.md",
        "Pseudocode.md",
        "Architecture.md",
        "Refinement.md",
        "Completion.md"
    ]
    for filename in expected_files:
        file_path = arch_dir / filename
        assert file_path.exists(), f"File {filename} was not created."
        # Check that the files are not empty
        assert file_path.stat().st_size > 0, f"File {filename} is empty."

    print("Test 1 passed: Architect mode generates architecture files successfully.")
import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_architect_mode_generates_files(clean_test_dir, cli_script):
    """Test that architect mode generates all expected architecture files."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Run the architect mode
    cmd = ["python", "sparc_cli.py", "architect"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result.returncode == 0, f"Architect mode failed: {result.stderr}"

    # Check that the architecture directory was created
    arch_dir = clean_test_dir / "architecture"
    assert arch_dir.exists(), "Architecture directory was not created."

    # Check that all expected files are present
    expected_files = [
        "Specification.md",
        "Pseudocode.md",
        "Architecture.md",
        "Refinement.md",
        "Completion.md"
    ]
    for filename in expected_files:
        file_path = arch_dir / filename
        assert file_path.exists(), f"File {filename} was not created."
        # Check that the files are not empty
        assert file_path.stat().st_size > 0, f"File {filename} is empty."

    print("Test 1 passed: Architect mode generates architecture files successfully.")
