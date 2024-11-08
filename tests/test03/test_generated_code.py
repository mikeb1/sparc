import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_generated_code_passes_tests(clean_test_dir, cli_script):
    """Test that generated code passes its own tests."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with a simple component
    guidance_content = """
[specification]
content = "Create a string utility that can reverse strings"

[architecture]
content = "## Component: StringUtils\\nProvides string manipulation utilities."
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run architect mode
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Run pytest on the generated code
    cmd_pytest = ["pytest", "tests"]
    result_pytest = subprocess.run(cmd_pytest, capture_output=True, text=True)
    assert result_pytest.returncode == 0, f"Generated code tests failed:\nstdout: {result_pytest.stdout}\nstderr: {result_pytest.stderr}"

    # Verify the generated files exist and have content
    src_file = clean_test_dir / "src" / "stringutils.py"
    test_file = clean_test_dir / "tests" / "test_stringutils.py"
    
    assert src_file.exists(), f"Source file {src_file} was not created"
    assert test_file.exists(), f"Test file {test_file} was not created"
    assert src_file.stat().st_size > 0, f"Source file {src_file} is empty"
    assert test_file.stat().st_size > 0, f"Test file {test_file} is empty"

    print("Test 3 passed: Generated code passes its own tests")
