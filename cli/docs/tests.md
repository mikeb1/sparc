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
from pathlib import Path

@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    # Create a temporary directory for the test
    test_dir = tmp_path_factory.mktemp("test03")
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

def test_generated_code_passes_tests(test_dir):
    # Copy the sparc_cli.py script and guidance.toml to the test directory
    base_dir = Path(__file__).resolve().parent.parent
    for filename in ["sparc_cli.py", "guidance.toml"]:
        src = base_dir / filename
        if src.exists():
            shutil.copy(src, test_dir)
        else:
            with open(test_dir / filename, 'w') as f:
                f.write("")

    os.chdir(test_dir)

    # Run the architect mode
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Run pytest to check if tests pass
    cmd_pytest = ["pytest", "tests"]
    result_pytest = subprocess.run(cmd_pytest, capture_output=True, text=True)
    assert result_pytest.returncode == 0, f"Generated code tests failed: {result_pytest.stderr}"

    print("Test 3 passed: Generated code passes tests.")
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