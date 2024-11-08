import os
import shutil
import subprocess
import pytest
import toml
from pathlib import Path

def test_guidance_file_customization(clean_test_dir, cli_script):
    """Test that guidance file content is properly used in generated files."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a custom guidance.toml file with specific content
    guidance = {
        "specification": {
            "content": "Create a logging system with different log levels and output formats."
        },
        "pseudocode": {
            "content": "Logger class with methods: debug(), info(), warn(), error()"
        },
        "architecture": {
            "content": "## Component: Logger\nHandles logging at different levels.\n\n## Component: LogFormatter\nFormats log messages."
        },
        "refinement": {
            "content": "Add timestamp and log rotation capabilities."
        },
        "completion": {
            "content": "Implement file and console output handlers."
        }
    }
    
    with open(clean_test_dir / "guidance.toml", "w") as f:
        toml.dump(guidance, f)

    # Run architect mode
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Verify that architecture files contain the custom guidance content
    arch_dir = clean_test_dir / "architecture"
    
    # Check Specification.md
    spec_content = (arch_dir / "Specification.md").read_text()
    assert "logging system" in spec_content.lower(), "Custom specification content not found"
    
    # Check Architecture.md
    arch_content = (arch_dir / "Architecture.md").read_text()
    assert "Component: Logger" in arch_content, "Logger component not found"
    assert "Component: LogFormatter" in arch_content, "LogFormatter component not found"
    
    # Check Refinement.md
    refine_content = (arch_dir / "Refinement.md").read_text()
    assert "timestamp" in refine_content.lower(), "Custom refinement content not found"
    
    # Run implement mode to verify components are created
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Verify component files were created
    expected_files = [
        "src/logger.py",
        "src/logformatter.py",
        "tests/test_logger.py",
        "tests/test_logformatter.py"
    ]
    
    for filepath in expected_files:
        full_path = clean_test_dir / filepath
        assert full_path.exists(), f"Expected file {filepath} was not created"
        assert full_path.stat().st_size > 0, f"File {filepath} is empty"

    print("Test 5 passed: Guidance file customization works correctly")
