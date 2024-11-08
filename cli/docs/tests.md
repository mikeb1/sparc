# Pytest Tests for the SPARC Development Application

## Introduction

The following provides a set of `pytest` tests designed to test the development of the previous SPARC application (`sparc_cli.py`) using the SPARC approach. Each test is outputted and ensures that the architecture and application are placed into a subfolder under `./tests/test[unit_test_id]`.

These tests will:

- Verify that the `sparc_cli.py` script functions correctly in both architect and implementation modes.
- Ensure that architecture files are generated as expected.
- Validate that components are correctly developed and that tests pass.

---

## Test Suite Structure

- **Test Directories**: Each test is placed in its own directory under `./tests/`, named `test[unit_test_id]` (e.g., `test01`, `test02`).
- **Isolation**: Tests are isolated from each other to prevent side effects.
- **Output**: Each test outputs logs and results to its own directory.

---

## Prerequisites

- **Python 3.x** installed.
- **pytest** installed:
  ```bash
  pip install pytest
  ```
- **aider.chat** installed and configured:
  ```bash
  pip install aider-chat
  ```
- **API Keys**: Ensure that any required API keys for `aider.chat` are set in your environment.

---

## Test 1: Test Architect Mode Generates Architecture Files

### Directory: `./tests/test01`

### Test Code: `test_architect_mode.py`

```python
import os
import shutil
import subprocess
import pytest
from pathlib import Path

@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    # Create a temporary directory for the test
    test_dir = tmp_path_factory.mktemp("test01")
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

def test_architect_mode_generates_files(test_dir):
    # Copy the sparc_cli.py script to the test directory
    script_path = Path(__file__).resolve().parent.parent / "sparc_cli.py"
    shutil.copy(script_path, test_dir)

    os.chdir(test_dir)

    # Run the architect mode
    cmd = ["python", "sparc_cli.py", "architect"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result.returncode == 0, f"Architect mode failed: {result.stderr}"

    # Check that the architecture directory was created
    arch_dir = test_dir / "architecture"
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
        # Optionally, check that the files are not empty
        assert file_path.stat().st_size > 0, f"File {filename} is empty."

    print("Test 1 passed: Architect mode generates architecture files successfully.")
```

### Instructions

1. **Navigate to the Test Directory**:

   ```bash
   cd tests/test01
   ```

2. **Run the Test**:

   ```bash
   pytest test_architect_mode.py
   ```

---

## Test 2: Test Implement Mode Develops Components

### Directory: `./tests/test02`

### Test Code: `test_implement_mode.py`

```python
import os
import shutil
import subprocess
import pytest
from pathlib import Path

@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    # Create a temporary directory for the test
    test_dir = tmp_path_factory.mktemp("test02")
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

def test_implement_mode_develops_components(test_dir):
    # Copy the sparc_cli.py script and guidance.toml to the test directory
    base_dir = Path(__file__).resolve().parent.parent
    for filename in ["sparc_cli.py", "guidance.toml"]:
        src = base_dir / filename
        if src.exists():
            shutil.copy(src, test_dir)
        else:
            with open(test_dir / filename, 'w') as f:
                f.write("")  # Create an empty guidance.toml if not present

    os.chdir(test_dir)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)

    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the src directory was created
    src_dir = test_dir / "src"
    assert src_dir.exists(), "Source directory was not created."

    # Check that the tests directory was created
    tests_dir = test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created."

    print("Test 2 passed: Implement mode develops components successfully.")
```

### Instructions

1. **Navigate to the Test Directory**:

   ```bash
   cd tests/test02
   ```

2. **Run the Test**:

   ```bash
   pytest test_implement_mode.py
   ```

---

## Test 3: Test Generated Code Passes Tests

### Directory: `./tests/test03`

### Test Code: `test_generated_code.py`

```python
import os
import shutil
import subprocess
import pytest
import venv
import time
import sys
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
                text=True,
                timeout=300  # 5 minute timeout for installations
            )
            
            if install_result.returncode != 0:
                logger.error(f"Dependency installation failed:\n{install_result.stderr}")
                logger.info("Attempting to fix dependencies...")
                _fix_dependencies(app_dir)
                attempt += 1
                time.sleep(5)  # Wait longer after dependency fixes
                continue

            # Run tests with proper Python path and coverage
            logger.info("Running tests with coverage...")
            env["PYTHONPATH"] = str(app_dir)
            result = subprocess.run(
                [
                    str(python_path), "-m", "pytest", "-v",
                    "--import-mode=importlib",
                    "--cov=src",
                    "--cov-report=xml:coverage_report.xml",
                    "--cov-report=term-missing"
                ],
                cwd=app_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout for tests
            )
            
            if result.returncode == 0:
                logger.info("All tests passed successfully!")
                logger.info("Generating test report...")
                _create_test_report(app_dir, True, result.stdout)
                return True
            
            logger.error(f"Test failures:\n{result.stdout}\n{result.stderr}")
            
            # Parse and fix specific errors
            if _fix_test_errors(app_dir, result.stdout + result.stderr):
                logger.info("Applied fixes, retrying verification...")
            else:
                logger.error("Could not automatically fix errors")
                logger.error("Full error trace:")
                logger.error(traceback.format_exc())
            
            _create_test_report(app_dir, False, result.stdout + result.stderr)
            
            attempt += 1
            if attempt < max_attempts:
                logger.info(f"Waiting before retry {attempt + 1}/{max_attempts}...")
                time.sleep(5)  # Increased wait time between attempts
                
        except subprocess.TimeoutExpired as e:
            logger.error(f"Timeout during {e.cmd} after {e.timeout} seconds")
            attempt += 1
        except Exception as e:
            logger.error(f"Verification attempt {attempt + 1} failed with error: {str(e)}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(5)
                continue
    
    logger.error(f"Application verification failed after {max_attempts} attempts")
    return False

def test_generated_code_passes_tests(test_dir):
    """Test that generated code works in a fresh virtual environment."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with comprehensive requirements
    guidance_content = """
[specification]
content = '''
Create a FastAPI REST API service with:
1. User Authentication:
   - JWT token-based authentication 
   - User registration and login endpoints
   - Password hashing with bcrypt
   - Token refresh mechanism

2. Data Models:
   - User model with email, hashed password, and profile info
   - SQLAlchemy ORM integration
   - SQLite database for storage
   - Pydantic schemas for request/response validation

3. API Features:
   - OpenAPI documentation
   - Input validation using Pydantic
   - Proper error handling with status codes
   - Rate limiting for API endpoints
   - CORS middleware configuration

4. Testing:
   - Unit tests for all endpoints
   - Integration tests with test database
   - Test fixtures and helpers
   - 100% code coverage target
'''

[architecture]
content = '''
## Component: AuthService
Handles user authentication and JWT operations:
- generate_jwt_token(user_data: dict) -> str
- verify_jwt_token(token: str) -> dict
- hash_password(password: str) -> str
- verify_password(plain_password: str, hashed_password: str) -> bool
- get_password_hash(password: str) -> str

## Component: UserService
Manages user operations:
- create_user(user_data: UserCreate) -> User
- get_user_by_email(email: str) -> User
- update_user(user_id: int, user_data: UserUpdate) -> User
- delete_user(user_id: int) -> bool
- get_users(skip: int = 0, limit: int = 100) -> List[User]

## Component: DatabaseService
Handles database operations:
- get_db() -> Generator[Session, None, None]
- init_db() -> None
- create_tables() -> None
- get_user_by_id(db: Session, user_id: int) -> User
- create_user_in_db(db: Session, user: UserCreate) -> User

## Component: ErrorHandler
Manages error responses:
- handle_validation_error(exc: ValidationError) -> JSONResponse
- handle_credentials_error() -> JSONResponse
- handle_not_found_error() -> JSONResponse
- handle_database_error(exc: SQLAlchemyError) -> JSONResponse
'''

[pseudocode]
content = '''
1. Database Setup:
   ```
   def init_db():
       create_engine(DATABASE_URL)
       create_database_tables()
       setup_migrations()
   ```

2. Authentication Flow:
   ```
   def login_user(email, password):
       user = find_user_by_email(email)
       if not user or not verify_password(password, user.hashed_password):
           raise InvalidCredentials
       return generate_jwt_token(user.id)
   ```

3. User Management:
   ```
   def register_user(user_data):
       validate_user_data(user_data)
       check_email_unique(user_data.email)
       hashed_password = hash_password(user_data.password)
       user = create_user_in_db(user_data, hashed_password)
       return user
   ```

4. API Routes:
   ```
   @app.post("/auth/register")
   def register(user_data: UserCreate):
       return register_user(user_data)

   @app.post("/auth/login")
   def login(credentials: LoginCredentials):
       return login_user(credentials)

   @app.get("/users/me")
   def get_current_user(token: str):
       return get_user_from_token(token)
   ```
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

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

    with open(test_output_dir / "README.md", "w") as f:
        f.write(report_content)

    assert verification_success, "Application verification failed after maximum attempts"
    
    print(f"\nVerified application saved to: {test_output_dir}")
    print("Test 3 passed: Generated code works in clean environment")
```

### Instructions

1. **Navigate to the Test Directory**:

   ```bash
   cd tests/test03
   ```

2. **Run the Test**:

   ```bash
   pytest test_generated_code.py
   ```

---

## Test 4: Test Component Detection from Architecture.md

### Directory: `./tests/test04`

### Test Code: `test_component_detection.py`

```python
import os
import shutil
import subprocess
import pytest
from pathlib import Path

@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    # Create a temporary directory for the test
    test_dir = tmp_path_factory.mktemp("test04")
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

def test_component_detection(test_dir):
    # Copy the sparc_cli.py script to the test directory
    script_path = Path(__file__).resolve().parent.parent / "sparc_cli.py"
    shutil.copy(script_path, test_dir)

    os.chdir(test_dir)

    # Create architecture directory and Architecture.md
    arch_dir = test_dir / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)

    architecture_md = arch_dir / "Architecture.md"
    architecture_content = """
    # Architecture

    ## Component: PaymentProcessor

    Handles payment processing.

    ## Component: UserAuth

    Manages user authentication.
    """
    with open(architecture_md, 'w') as f:
        f.write(architecture_content)

    # Run the implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the components were detected and files created
    expected_files = [
        test_dir / "src" / "paymentprocessor.py",
        test_dir / "src" / "userauth.py",
        test_dir / "tests" / "test_paymentprocessor.py",
        test_dir / "tests" / "test_userauth.py",
    ]
    for file_path in expected_files:
        assert file_path.exists(), f"Expected file {file_path} was not created."

    print("Test 4 passed: Component detection from Architecture.md works.")
```

### Instructions

1. **Navigate to the Test Directory**:

   ```bash
   cd tests/test04
   ```

2. **Run the Test**:

   ```bash
   pytest test_component_detection.py
   ```

---

## Test 5: Test Guidance File Customization

### Directory: `./tests/test05`

### Test Code: `test_guidance_file.py`

```python
import os
import shutil
import subprocess
import pytest
from pathlib import Path
import toml

@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    # Create a temporary directory for the test
    test_dir = tmp_path_factory.mktemp("test05")
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

def test_guidance_file_customization(test_dir):
    # Copy the sparc_cli.py script to the test directory
    script_path = Path(__file__).resolve().parent.parent / "sparc_cli.py"
    shutil.copy(script_path, test_dir)

    os.chdir(test_dir)

    # Create a custom guidance.toml file
    guidance = {
        "specification": {
            "content": "Create a detailed specification for a blog platform with user registration, post creation, and commenting."
        },
        "pseudocode": {
            "content": "Provide high-level pseudocode focusing on the interaction between UserAuth, PostManager, and CommentManager."
        },
        "architecture": {
            "content": "Describe the system architecture with components: UserAuth, PostManager, CommentManager."
        },
        "refinement": {
            "content": "Discuss optimization strategies for database access and caching."
        },
        "completion": {
            "content": "Finalize deployment strategies and scaling considerations."
        }
    }
    guidance_toml = test_dir / "guidance.toml"
    with open(guidance_toml, 'w') as f:
        toml.dump(guidance, f)

    # Run the architect mode
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Check that the architecture files contain the custom guidance
    arch_dir = test_dir / "architecture"
    spec_file = arch_dir / "Specification.md"
    assert spec_file.exists(), "Specification.md was not created."
    with open(spec_file, 'r') as f:
        content = f.read()
        assert "blog platform" in content, "Custom guidance not found in Specification.md."

    print("Test 5 passed: Guidance file customization works.")
```

### Instructions

1. **Navigate to the Test Directory**:

   ```bash
   cd tests/test05
   ```

2. **Run the Test**:

   ```bash
   pytest test_guidance_file.py
   ```

---

## Running All Tests

To run all tests at once, navigate to the `tests` directory and execute:

```bash
pytest
```

---

## Notes

- **Isolation**: Each test uses a temporary directory to avoid interfering with other tests or the main project.
- **Dependencies**: Ensure all dependencies (`aider-chat`, `pytest`, `toml`) are installed before running the tests.
- **API Keys**: The tests that invoke `aider.chat` require valid API keys and network access.

---

## Conclusion

These tests verify the functionality of the SPARC development application using the SPARC approach. By organizing tests into subfolders and outputting each test, we ensure clarity and maintainability. Adjust and extend these tests as needed to cover additional functionality or edge cases.
