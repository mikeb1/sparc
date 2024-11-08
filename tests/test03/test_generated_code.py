import os
import shutil
import subprocess
import pytest
import venv
import sys
import time
import logging
import traceback
import json
from pathlib import Path
from datetime import datetime
from litellm import completion

logger = logging.getLogger(__name__)

async def generate_architecture_files(arch_dir: Path, guidance: dict) -> bool:
    """Generate architecture files using AI assistance."""
    try:
        response = await completion(
            model="claude-3-sonnet-20240229",
            messages=[{
                "role": "user", 
                "content": f"""Given this project guidance, generate detailed architecture files:

Guidance:
{json.dumps(guidance, indent=2)}

Please generate content for:
1. Specification.md - Detailed requirements and constraints
2. Architecture.md - Component design and interactions
3. Pseudocode.md - Implementation approach
4. Refinement.md - Optimization and improvements
5. Completion.md - Verification criteria

Focus on creating a robust FastAPI application with proper error handling, testing, and security."""
            }],
            temperature=0.2,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        files = {
            "Specification.md": content.split("# Architecture.md")[0],
            "Architecture.md": content.split("# Architecture.md")[1].split("# Pseudocode.md")[0],
            "Pseudocode.md": content.split("# Pseudocode.md")[1].split("# Refinement.md")[0],
            "Refinement.md": content.split("# Refinement.md")[1].split("# Completion.md")[0],
            "Completion.md": content.split("# Completion.md")[1]
        }
        
        for filename, content in files.items():
            file_path = arch_dir / filename
            file_path.write_text(content.strip())
            logger.info(f"Generated {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to generate architecture files: {str(e)}")
        return False

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

def verify_application(app_dir: Path, python_path: Path, env: dict, max_attempts: int = 3) -> bool:
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
litellm>=1.0.0
"""
        with open(app_dir / "requirements.txt", "w") as f:
            f.write(requirements.strip())

    attempt = 0
    while attempt < max_attempts:
        try:
            logger.info(f"\nVerification attempt {attempt + 1}/{max_attempts}")
            
            # Install requirements
            logger.info("Installing dependencies...")
            install_result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=app_dir,
                env=env,
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                logger.error(f"Dependency installation failed:\n{install_result.stderr}")
                logger.info("Attempting to fix dependencies...")
                # Try to fix dependencies by running implement mode with --fix-deps
                subprocess.run(
                    ["python", "sparc_cli.py", "implement", "--fix-deps"],
                    cwd=app_dir,
                    capture_output=True,
                    text=True
                )
            else:
                logger.info("Dependencies installed successfully")
            
            # Run tests with proper Python path
            logger.info("Running tests...")
            env["PYTHONPATH"] = str(app_dir)
            result = subprocess.run(
                [str(python_path), "-m", "pytest", "-v", "--import-mode=importlib"],
                cwd=app_dir,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True
                
            # If tests failed, try to fix issues
            fix_cmd = ["python", "sparc_cli.py", "implement", "--fix-issues"]
            fix_result = subprocess.run(
                fix_cmd,
                cwd=app_dir,
                capture_output=True,
                text=True
            )
            
            if fix_result.returncode == 0:
                logger.info("Fixes applied, retrying verification...")
            else:
                logger.error(f"Fix attempt failed:\n{fix_result.stderr}")
            
            attempt += 1
            if attempt < max_attempts:
                logger.info(f"Waiting before retry {attempt + 1}/{max_attempts}...")
                time.sleep(3)  # Increased wait time between attempts
                
        except Exception as e:
            logger.error(f"Verification attempt {attempt + 1} failed with error: {str(e)}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            attempt += 1
            if attempt < max_attempts:
                logger.info(f"Waiting before retry {attempt + 1}/{max_attempts}...")
                time.sleep(3)
    
    logger.error(f"Application verification failed after {max_attempts} attempts")
    return False

@pytest.mark.asyncio
async def test_generated_code_passes_tests(clean_test_dir, cli_script, output_dir):
    """Test that generated code works in a fresh virtual environment."""
    try:
        # Copy the sparc_cli.py script to the test directory
        shutil.copy(cli_script, clean_test_dir)
        
        os.chdir(clean_test_dir)

        # Generate architecture files with AI assistance
        arch_dir = clean_test_dir / "architecture"
        arch_dir.mkdir(exist_ok=True)
        
        # Define guidance for architecture generation
        guidance = {
            "specification": {
                "content": "Create a FastAPI REST service with user authentication and CRUD operations"
            },
            "architecture": {
                "content": "Define core components for auth, database, and error handling"
            },
            "pseudocode": {
                "content": "Outline key functions and data flows between components"
            }
        }
        
        success = await generate_architecture_files(arch_dir, guidance)
        assert success, "Failed to generate architecture files"

        # Create a basic guidance.toml file
        guidance_content = """
[specification]
content = '''
Create a FastAPI REST service with:
- User authentication using JWT tokens
- SQLite database for storage
- Input validation using Pydantic
'''

[architecture]
content = '''
## Component: AuthService
Handles JWT token generation and validation.

## Component: UserService
Manages user operations and data.

## Component: DatabaseService
Handles database operations and connections.
'''
"""
        with open(clean_test_dir / "guidance.toml", "w") as f:
            f.write(guidance_content)

        # Run architect and implement modes
        logger.info("Running architect mode...")
        subprocess.run(["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"], check=True)
        logger.info("Running implement mode...")
        subprocess.run(["python", "sparc_cli.py", "implement", "--guidance-file", "guidance.toml"], check=True)

        # Create virtual environment for testing
        venv_path = clean_test_dir / ".venv"
        logger.info(f"Creating virtual environment at {venv_path}")
        env, python_path = create_and_activate_venv(venv_path)

        # Verify application with increased attempts and better error handling
        verification_success = verify_application(clean_test_dir, python_path, env, max_attempts=5)
        
        # Save test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_output_dir = output_dir / f"verified_app_{timestamp}"
        logger.info(f"Saving test results to {test_output_dir}")
        
        shutil.copytree(clean_test_dir, test_output_dir)
        
        # Create detailed test report
        _create_test_report(test_output_dir, verification_success, venv_path, python_path)

        assert verification_success, "Application verification failed after maximum attempts"
        
        print(f"\nVerified application saved to: {test_output_dir}")
        print("Test 3 passed: Generated code works in clean environment")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise
    
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
def _fix_dependencies(app_dir: Path) -> None:
    """Fix common dependency issues."""
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

async def analyze_error_with_ai(error_output: str, files: dict) -> dict:
    """Use Claude 3.5 Sonnet to analyze errors and suggest fixes."""
    from litellm import completion
    
    prompt = f"""You are an expert Python developer analyzing test failures in a FastAPI application.
Please analyze this error output and the relevant source files to suggest specific fixes:

Error Output:
{error_output}

Source Files:
{files}

Please provide:
1. Root cause analysis
2. Specific code changes needed
3. Additional context or warnings
4. Suggested test improvements

Format your response as a JSON object with these keys:
- root_cause: str
- code_changes: dict[str, str] (filename -> suggested changes)
- context: str
- test_improvements: str
"""

    try:
        response = await completion(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return None

async def _fix_test_errors(app_dir: Path, error_output: str) -> bool:
    """Parse test errors and apply fixes using AI assistance."""
    fixed = False
    
    try:
        # Collect relevant files for analysis
        files = {}
        for file_pattern in ["src/*.py", "tests/test_*.py"]:
            for file_path in app_dir.glob(file_pattern):
                try:
                    files[str(file_path)] = file_path.read_text()
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {str(e)}")
        
        # Get AI analysis
        analysis = await analyze_error_with_ai(error_output, files)
        if not analysis:
            return fixed
        
        fixes = json.loads(analysis)
        logger.info(f"AI Analysis: {fixes['root_cause']}")
        
        # Apply suggested code changes
        for filename, changes in fixes['code_changes'].items():
            file_path = app_dir / filename
            if file_path.exists():
                logger.info(f"Applying changes to {filename}")
                file_path.write_text(changes)
                fixed = True
        
        # Log additional context and improvements
        logger.info(f"Context: {fixes['context']}")
        logger.info(f"Suggested test improvements: {fixes['test_improvements']}")
        
        # Fix common issues
        if "DatabaseService" in error_output:
            db_service_path = app_dir / "src" / "databaseservice.py"
            if db_service_path.exists():
                content = db_service_path.read_text()
                if "class DatabaseService:" not in content:
                    new_content = """from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def init_db() -> None:
        Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    return DatabaseService.get_db()
"""
                    db_service_path.write_text(new_content)
                    fixed = True
                    logger.info("Fixed DatabaseService class definition")

        # Fix relative imports
        if "ImportError" in error_output and "cannot import name" in error_output:
            for py_file in (app_dir / "tests").glob("test_*.py"):
                content = py_file.read_text()
                if "from ." in content:
                    new_content = content.replace("from .", "from src.")
                    py_file.write_text(new_content)
                    fixed = True
                    logger.info(f"Fixed relative imports in {py_file.name}")

        # Create __init__.py files if missing
        for dir_path in [app_dir / "src", app_dir / "tests"]:
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                fixed = True
                logger.info(f"Created {init_file}")

    except Exception as e:
        logger.error(f"Error while fixing tests: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        return fixed

    return fixed

def _create_test_report(test_output_dir: Path, verification_success: bool, venv_path: Path, python_path: Path) -> None:
    """Create a detailed test report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_content = f"""# Test Verification Report - {timestamp}

## Test Status
- Verification Success: {'Yes' if verification_success else 'No'}
- Maximum Attempts: 5
- Virtual Environment: {venv_path}
- Python Version: {sys.version}

## Components Tested
{_get_component_list(test_output_dir)}

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
