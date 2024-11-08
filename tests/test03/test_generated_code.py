import os
import shutil
import subprocess
import pytest
import venv
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def create_and_activate_venv(venv_path: Path) -> tuple[dict, Path]:
    """Create a virtual environment and return the environment variables needed to use it."""
    venv.create(venv_path, with_pip=True)
    
    # Get path to activation scripts
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_path = venv_path / "bin" / "python"

    # Create environment variables dict
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = str(venv_path / "bin") + os.pathsep + env["PATH"]
    
    return env, python_path

def verify_application(app_dir: Path, python_path: Path, env: dict, max_attempts: int = 5) -> bool:
    """Verify the application works by installing dependencies and running tests."""
    # Create requirements.txt if it doesn't exist
    if not (app_dir / "requirements.txt").exists():
        requirements = """
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.23
pydantic>=1.8.2
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
pytest>=6.2.4
httpx>=0.18.2
pytest-cov>=2.12.1
alembic>=1.7.1
email-validator>=2.0.0
python-dotenv>=1.0.0
"""
        with open(app_dir / "requirements.txt", "w") as f:
            f.write(requirements.strip())

    attempt = 0
    while attempt < max_attempts:
        try:
            # Install requirements
            subprocess.run(
                [str(python_path), "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=app_dir,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Run tests with correct Python path and verbose output
            env["PYTHONPATH"] = f"{str(app_dir)}/src:{str(app_dir)}/tests"
            result = subprocess.run(
                [str(python_path), "-m", "pytest", "-v", "--import-mode=importlib", "--tb=short"],
                cwd=app_dir,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("All tests passed successfully!")
                return True
            
            logger.error(f"Test failures:\n{result.stdout}\n{result.stderr}")
            
            # If tests failed, try to fix issues
            logger.info("Attempting to fix test failures...")
            fix_cmd = ["python", "sparc_cli.py", "implement", "--fix-issues", "--model", "claude-3-sonnet-20240229"]
            fix_result = subprocess.run(
                fix_cmd,
                cwd=app_dir,
                capture_output=True,
                text=True
            )
            
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)  # Wait before retrying
                
        except Exception as e:
            logger.error(f"Verification attempt {attempt + 1} failed: {str(e)}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)
    
    return False

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

    # Run architect and implement modes with enhanced logging
    logger.info("Running architect mode...")
    subprocess.run(["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"], check=True)
    logger.info("Running implement mode...")
    subprocess.run(["python", "sparc_cli.py", "implement", "--guidance-file", "guidance.toml"], check=True)

    # Create virtual environment for testing
    venv_path = clean_test_dir / ".venv"
    logger.info(f"Creating virtual environment at {venv_path}")
    env, python_path = create_and_activate_venv(venv_path)

    # Verify application with increased attempts and logging
    verification_success = verify_application(clean_test_dir, python_path, env, max_attempts=5)
    
    # Save detailed test results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_output_dir = output_dir / f"verified_app_{timestamp}"
    logger.info(f"Saving test results to {test_output_dir}")
    
    # Copy the generated and verified application
    shutil.copytree(clean_test_dir, test_output_dir)
    
    # Create a comprehensive test report
    report_content = f"""# Test Verification Report - {timestamp}

## Test Status
- Verification Success: {'Yes' if verification_success else 'No'}
- Maximum Attempts: 5
- Virtual Environment: {venv_path}
- Python Version: {sys.version}

## Components Tested
{_get_component_list(clean_test_dir)}

## Test Results
- Dependencies: {'Successfully installed' if verification_success else 'Installation issues encountered'}
- Tests: {'All passing' if verification_success else 'Some failures detected'}
- Coverage: See coverage_report.xml for details

## Generated Files
- Source Code: src/
- Test Suite: tests/
- Architecture: architecture/
- Dependencies: requirements.txt

## Next Steps
{_get_next_steps(verification_success)}

## Test Environment
- OS: {os.name}
- Platform: {sys.platform}
- Python Path: {python_path}
"""
    
    with open(test_output_dir / "README.md", "w") as f:
        f.write(report_content)

    assert verification_success, "Application verification failed after maximum attempts"
    
    print(f"\nVerified application saved to: {test_output_dir}")
    print("Test 3 passed: Generated code works in clean environment")
def _get_component_list(app_dir: Path) -> str:
    """Get a formatted list of components that were tested."""
    src_dir = app_dir / "src"
    components = []
    if src_dir.exists():
        for file in src_dir.glob("*.py"):
            if file.stem != "__init__":
                components.append(f"- {file.stem}")
    return "\n".join(components) if components else "No components found"

def _get_next_steps(success: bool) -> str:
    """Get recommended next steps based on test results."""
    if success:
        return """
1. Review test coverage reports
2. Consider adding more test cases
3. Proceed with deployment preparations
"""
    else:
        return """
1. Review test failure logs
2. Check component dependencies
3. Verify test environment setup
4. Run tests individually to isolate failures
5. Consider increasing test timeout values
"""
