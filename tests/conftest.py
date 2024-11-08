import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the root directory of the repository."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def output_dir(repo_root):
    """Create and manage the permanent test outputs directory."""
    output_dir = repo_root / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Clear existing test outputs except .gitkeep
    for item in output_dir.iterdir():
        if item.name != '.gitkeep':
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
                
    return output_dir

@pytest.fixture(scope="session")
def cli_script(repo_root):
    """Return path to the CLI script."""
    return repo_root / "cli" / "sparc_cli.py"

@pytest.fixture
def clean_test_dir(tmp_path):
    """Create a clean test directory for each test."""
    yield tmp_path
    # Cleanup after test
    shutil.rmtree(tmp_path)
import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the root directory of the repository."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def cli_script(repo_root):
    """Return path to the CLI script."""
    return repo_root / "cli" / "sparc_cli.py"

@pytest.fixture
def clean_test_dir(tmp_path):
    """Create a clean test directory for each test."""
    yield tmp_path
    # Cleanup after test
    shutil.rmtree(tmp_path)
