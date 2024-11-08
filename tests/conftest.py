import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the root directory of the repository."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def output_dir(repo_root):
    """Create a permanent directory for test outputs."""
    output_dir = repo_root / "test_outputs"
    output_dir.mkdir(exist_ok=True)
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
