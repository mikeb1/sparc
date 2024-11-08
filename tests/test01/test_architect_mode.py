import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_architect_mode_generates_files(clean_test_dir, cli_script, output_dir):
    """Test that architect mode generates files and saves them to output directory."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml with real project requirements
    guidance_content = """
[specification]
content = '''
Create a simple REST API service with:
- User authentication
- CRUD operations for a resource
- Basic error handling
'''

[architecture]
content = '''
## Component: AuthService
Handles user authentication and authorization.

## Component: ResourceManager 
Manages CRUD operations for resources.

## Component: ErrorHandler
Provides standardized error handling.
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode with aider integration using Claude 3.5 Sonnet
    cmd = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml", "--model", "claude-3-sonnet-20240229"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result.returncode == 0, f"Architect mode failed: {result.stderr}"

    # Print the output for debugging
    print("\nArchitect mode output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

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

    # After successful generation, copy results to output directory
    test_output_dir = output_dir / "test01_architect_output"
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    shutil.copytree(clean_test_dir, test_output_dir)
    
    print(f"\nArchitect mode output saved to: {test_output_dir}")
    # After successful generation, copy results to output directory
    test_output_dir = output_dir / "test01_architect_output"
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    shutil.copytree(clean_test_dir, test_output_dir)
    
    print(f"\nArchitect mode output saved to: {test_output_dir}")
    print("Test 1 passed: Architect mode generates architecture files successfully.")
import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_architect_mode_generates_files(clean_test_dir, cli_script, output_dir):
    """Test that architect mode generates files and saves them to output directory."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml with real project requirements
    guidance_content = """
[specification]
content = '''
Create a simple REST API service with:
- User authentication
- CRUD operations for a resource
- Basic error handling
'''

[architecture]
content = '''
## Component: AuthService
Handles user authentication and authorization.

## Component: ResourceManager 
Manages CRUD operations for resources.

## Component: ErrorHandler
Provides standardized error handling.
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode with aider integration using Claude 3.5 Sonnet
    cmd = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml", "--model", "claude-3-sonnet-20240229"]
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
