import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_implement_mode_develops_components(clean_test_dir, cli_script, output_dir):
    """Test that implement mode develops components and saves them to output directory."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with real implementation requirements
    guidance_content = """
[specification]
content = '''
Create a REST API service with:
- User authentication using JWT tokens
- CRUD operations for a blog post resource
- Error handling with proper HTTP status codes
'''

[architecture]
content = '''
## Component: AuthService
Handles JWT token generation, validation, and user authentication.

## Component: BlogPostManager
Manages CRUD operations for blog posts with proper validation.

## Component: ErrorHandler
Provides standardized error handling with appropriate HTTP status codes.
'''

[pseudocode]
content = '''
AuthService:
- generate_token(user_data) -> str
- validate_token(token) -> dict
- authenticate_user(username, password) -> bool

BlogPostManager:
- create_post(user_id, title, content) -> Post
- get_post(post_id) -> Post
- update_post(post_id, updates) -> Post
- delete_post(post_id) -> bool

ErrorHandler:
- handle_auth_error() -> Response(401)
- handle_not_found() -> Response(404)
- handle_validation_error() -> Response(400)
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode with Claude 3.5 Sonnet
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml", "--model", "claude-3-sonnet-20240229"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the src directory was created
    src_dir = clean_test_dir / "src"
    assert src_dir.exists(), "Source directory was not created"

    # Check that the tests directory was created
    tests_dir = clean_test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created"

    # Check that the src directory was created
    src_dir = clean_test_dir / "src"
    assert src_dir.exists(), "Source directory was not created"

    # Check that the tests directory was created
    tests_dir = clean_test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created"

    # After successful generation, copy results to output directory
    test_output_dir = output_dir / "test02_implement_output"
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    shutil.copytree(clean_test_dir, test_output_dir)
    
    print(f"\nImplement mode output saved to: {test_output_dir}")
    print("Test 2 passed: Implement mode develops components successfully")

    # After successful generation, copy results to output directory
    test_output_dir = output_dir / "test02_implement_output"
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    shutil.copytree(clean_test_dir, test_output_dir)
    
    print(f"\nImplement mode output saved to: {test_output_dir}")
    print("Test 2 passed: Implement mode develops components successfully")
import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_implement_mode_develops_components(clean_test_dir, cli_script, output_dir):
    """Test that implement mode develops components and saves them to output directory."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with real implementation requirements
    guidance_content = """
[specification]
content = '''
Create a REST API service with:
- User authentication using JWT tokens
- CRUD operations for a blog post resource
- Error handling with proper HTTP status codes
'''

[architecture]
content = '''
## Component: AuthService
Handles JWT token generation, validation, and user authentication.

## Component: BlogPostManager
Manages CRUD operations for blog posts with proper validation.

## Component: ErrorHandler
Provides standardized error handling with appropriate HTTP status codes.
'''

[pseudocode]
content = '''
AuthService:
- generate_token(user_data) -> str
- validate_token(token) -> dict
- authenticate_user(username, password) -> bool

BlogPostManager:
- create_post(user_id, title, content) -> Post
- get_post(post_id) -> Post
- update_post(post_id, updates) -> Post
- delete_post(post_id) -> bool

ErrorHandler:
- handle_auth_error() -> Response(401)
- handle_not_found() -> Response(404)
- handle_validation_error() -> Response(400)
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode with Claude 3.5 Sonnet
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml", "--model", "claude-3-sonnet-20240229"]
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
