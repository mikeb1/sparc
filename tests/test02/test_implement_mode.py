import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_implement_mode_develops_components(clean_test_dir, cli_script):
    """Test that implement mode develops components successfully."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file
    guidance_content = """
[specification]
content = "Create a simple calculator application"

[architecture]
content = "## Component: Calculator\\nHandles basic math operations."
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the src directory was created
    src_dir = clean_test_dir / "src"
    assert src_dir.exists(), "Source directory was not created"

    # Check that the tests directory was created
    tests_dir = clean_test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created"

    # Check for expected component files
    calculator_file = src_dir / "calculator.py"
    calculator_test = tests_dir / "test_calculator.py"
    assert calculator_file.exists(), "Calculator component file was not created"
    assert calculator_test.exists(), "Calculator test file was not created"

    print("Test 2 passed: Implement mode develops components successfully")
import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_implement_mode_develops_components(clean_test_dir, cli_script):
    """Test that implement mode develops components successfully."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file
    guidance_content = """
[specification]
content = "Create a simple calculator application"

[architecture]
content = "## Component: Calculator\\nHandles basic math operations."
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the src directory was created
    src_dir = clean_test_dir / "src"
    assert src_dir.exists(), "Source directory was not created"

    # Check that the tests directory was created
    tests_dir = clean_test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created"

    # Check for expected component files
    calculator_file = src_dir / "calculator.py"
    calculator_test = tests_dir / "test_calculator.py"
    assert calculator_file.exists(), "Calculator component file was not created"
    assert calculator_test.exists(), "Calculator test file was not created"

    print("Test 2 passed: Implement mode develops components successfully")
