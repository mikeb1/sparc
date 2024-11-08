import os
import shutil
import subprocess
import pytest
from pathlib import Path

def test_generated_code_passes_tests(clean_test_dir, cli_script, output_dir):
    """Test that generated code works in a fresh virtual environment."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with a real REST API
    guidance_content = """
[specification]
content = '''
Create a FastAPI REST service with:
- User registration and login endpoints
- JWT token authentication
- SQLite database for storage
- Input validation using Pydantic
'''

[architecture]
content = '''
## Component: AuthService
Handles user authentication and JWT tokens.

## Component: UserService
Manages user registration and profile data.

## Component: DatabaseService
Handles SQLite database operations.
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Create requirements.txt
    requirements = """
fastapi>=0.68.0
uvicorn>=0.15.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
SQLAlchemy>=1.4.23
pytest>=6.2.4
httpx>=0.18.2
"""
    with open(clean_test_dir / "requirements.txt", "w") as f:
        f.write(requirements)

    # Run architect and implement modes
    subprocess.run(["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"], check=True)
    subprocess.run(["python", "sparc_cli.py", "implement", "--guidance-file", "guidance.toml"], check=True)

    # Create virtual environment for testing
    venv_path = clean_test_dir / ".venv"
    env, python_path = create_and_activate_venv(venv_path)

    # Verify application works
    verification_success = verify_application(clean_test_dir, python_path, env)
    
    # Save test output with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_output_dir = output_dir / f"verified_app_{timestamp}"
    
    # Copy the generated and verified application
    shutil.copytree(clean_test_dir, test_output_dir)
    
    # Create a detailed README.md with verification results
    readme_content = f"""# FastAPI Application - Generated {timestamp}

This REST API application was generated and verified using the SPARC framework.

## Components
- AuthService: JWT authentication and token management
- UserService: User registration and profile management  
- DatabaseService: SQLite database operations

## Verification Status
- Virtual Environment: Created successfully
- Dependencies: {'Installed successfully' if verification_success else 'Installation issues encountered'}
- Tests: {'All tests passing' if verification_success else 'Some tests failed'}

## Generated Files
- src/: Source code for each component
- tests/: Unit tests for each component
- architecture/: SPARC architecture documents
- requirements.txt: Project dependencies

## API Endpoints
- POST /auth/register: Register new user
- POST /auth/login: Login and get JWT token
- GET /users/me: Get current user profile

## Verification Log
The application was verified in a clean virtual environment.
Maximum verification attempts: 3
Final status: {'Success' if verification_success else 'Failed'}
"""
    
    with open(test_output_dir / "README.md", "w") as f:
        f.write(readme_content)

    assert verification_success, "Application verification failed after maximum attempts"
    
    print(f"\nVerified application saved to: {test_output_dir}")
    print("Test 3 passed: Generated code works in clean environment")
