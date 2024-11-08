import os
import shutil
import subprocess
import pytest
from pathlib import Path
from datetime import datetime

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

    # Save to test_outputs with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_output_dir = output_dir / f"architecture_{timestamp}"
    
    # Copy the generated architecture to test_outputs
    shutil.copytree(clean_test_dir, test_output_dir)
    
    # Create a README.md in the output directory
    readme_content = f"""# Architecture Documents - Generated {timestamp}

This set of architecture documents was automatically generated using the SPARC framework.

## Generated Files
- Specification.md: Detailed project requirements
- Architecture.md: System architecture and components
- Pseudocode.md: High-level implementation details
- Refinement.md: Design refinements and decisions
- Completion.md: Project completion criteria

## Components Identified
- AuthService
- ResourceManager
- ErrorHandler

Generated using guidance from guidance.toml
"""
    
    with open(test_output_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"\nArchitecture documents saved to: {test_output_dir}")
    print("Test 1 passed: Architect mode generates architecture files successfully.")
