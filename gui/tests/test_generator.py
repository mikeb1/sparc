import pytest
import pytest_asyncio
import asyncio
import warnings
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging

# Filter out litellm deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="litellm.utils")

# Configure logging for better debugging output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure pytest-asyncio
pytest.register_assert_rewrite('pytest_asyncio')
pytestmark = pytest.mark.asyncio

from gui.streamlit.utils.generator import (
    generate_sparc_content,
    detect_tech_stack_from_description
)

# Mock responses for different completion calls
MOCK_TECH_STACK_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content='{"framework": "Next.js", "language": "typescript", "features": ["authentication", "database", "api"]}'
            )
        )
    ]
)

MOCK_SPECIFICATION_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Specification Content\n\nThis is mock generated specification content."
            )
        )
    ]
)

MOCK_ARCHITECTURE_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Architecture Content\n\nThis is mock generated architecture content."
            )
        )
    ]
)

MOCK_PSEUDOCODE_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Pseudocode Content\n\nThis is mock generated pseudocode content."
            )
        )
    ]
)

MOCK_REFINEMENT_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Refinement Content\n\nThis is mock generated refinement content."
            )
        )
    ]
)

MOCK_COMPLETION_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Completion Content\n\nThis is mock generated completion content."
            )
        )
    ]
)

@pytest.fixture
def mock_completion():
    """Mock the completion function to return predefined responses."""
    with patch('gui.streamlit.utils.generator.completion') as mock:
        async def async_mock(*args, **kwargs):
            messages = kwargs.get('messages', [])
            for msg in messages:
                content = msg.get('content', '')
                if 'Extract tech stack from' in content:
                    return MOCK_TECH_STACK_RESPONSE
                
            # Return specific mock content based on the file being generated
            if 'Specification.md' in content:
                return MOCK_SPECIFICATION_RESPONSE
            elif 'Architecture.md' in content:
                return MOCK_ARCHITECTURE_RESPONSE
            elif 'Pseudocode.md' in content:
                return MOCK_PSEUDOCODE_RESPONSE
            elif 'Refinement.md' in content:
                return MOCK_REFINEMENT_RESPONSE
            elif 'Completion.md' in content:
                return MOCK_COMPLETION_RESPONSE
            
            # Default response for other cases
            return MOCK_COMPLETION_RESPONSE
        mock.side_effect = async_mock
        yield mock

@pytest.mark.asyncio
async def test_detect_tech_stack_from_description(mock_completion):
    """
    Test tech stack detection from project description.
    """
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"

    tech_stack = await detect_tech_stack_from_description(project_desc, model)

    assert tech_stack["framework"] == "Next.js", "Framework should be Next.js"
    assert tech_stack["language"] == "typescript", "Language should be TypeScript"
    assert "authentication" in tech_stack["features"], "Feature 'authentication' should be included"
    assert "database" in tech_stack["features"], "Feature 'database' should be included"
    assert "api" in tech_stack["features"], "Feature 'api' should be included"

@pytest.mark.asyncio
async def test_generate_sparc_content(mock_completion):
    """
    Test SPARC content generation.
    Ensures that all expected files are generated with correct content.
    """
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"

    files_content = await generate_sparc_content(project_desc, model)

    # Define expected content for each file
    expected_files = {
        "Specification.md": "# Specification Content\n\nThis is mock generated specification content.",
        "Architecture.md": "# Architecture Content\n\nThis is mock generated architecture content.",
        "Pseudocode.md": "# Pseudocode Content\n\nThis is mock generated pseudocode content.",
        "Refinement.md": "# Refinement Content\n\nThis is mock generated refinement content.",
        "Completion.md": "# Completion Content\n\nThis is mock generated completion content.",
    }

    # Verify that each expected file is present and has the correct content
    for filename, expected_content in expected_files.items():
        assert filename in files_content, f"Missing file: {filename}"
        actual_content = files_content[filename]
        assert actual_content == expected_content, f"Unexpected content in {filename}: Expected '{expected_content}', got '{actual_content}'"

    # Verify 'guidance.toml' separately
    assert "guidance.toml" in files_content, "Missing file: guidance.toml"
    guidance_content = files_content["guidance.toml"]
    expected_guidance = (
        '[project]\n'
        'framework = "Next.js"\n'
        'language = "typescript"\n'
        'features = [ "authentication", "database", "api",]\n\n'
        '[specification]\n'
        'content = "# Specification Content\\n\\nThis is mock generated specification content."\n'
    )
    assert guidance_content == expected_guidance, "Unexpected content in guidance.toml"

    # Additional checks to ensure tech stack information is present
    assert "Next.js" in guidance_content, "guidance.toml should contain 'Next.js'"
    assert "typescript" in guidance_content, "guidance.toml should contain 'typescript'"

@pytest.mark.asyncio
async def test_generate_sparc_content_error_handling():
    """
    Test error handling in SPARC content generation.
    Ensures that exceptions are properly raised and handled.
    """
    with patch('gui.streamlit.utils.generator.completion', side_effect=Exception("API Error")):
        project_desc = "Build a Next.js web application with TypeScript"
        model = "claude-3-sonnet-20240229"

        with pytest.raises(Exception) as exc_info:
            await generate_sparc_content(project_desc, model)

        assert "API Error" in str(exc_info.value), "Exception message should contain 'API Error'"

@pytest.mark.asyncio
async def test_file_structure(mock_completion, tmp_path):
    """
    Test that generated files follow the expected structure.
    Writes files to a temporary directory and verifies their existence and content.
    """
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"

    files_content = await generate_sparc_content(project_desc, model)

    # Write files to temporary directory and verify
    for filename, content in files_content.items():
        file_path = tmp_path / filename
        logger.debug(f"Writing to temporary file: {file_path}")
        file_path.write_text(content)

        # Verify file exists
        assert file_path.exists(), f"File {filename} does not exist in the temporary directory."

        # Verify file is not empty
        assert file_path.stat().st_size > 0, f"File {filename} is empty."

        # Optionally, verify the content matches expected
        if filename == "guidance.toml":
            expected_content = (
                '[project]\n'
                'framework = "Next.js"\n'
                'language = "typescript"\n'
                'features = [ "authentication", "database", "api",]\n\n'
                '[specification]\n'
                'content = "# Specification Content\\n\\nThis is mock generated specification content."\n'
            )
            assert file_path.read_text() == expected_content, f"Unexpected content in {filename}"
        else:
            expected_content = {
                "Specification.md": "# Specification Content\n\nThis is mock generated specification content.",
                "Architecture.md": "# Architecture Content\n\nThis is mock generated architecture content.",
                "Pseudocode.md": "# Pseudocode Content\n\nThis is mock generated pseudocode content.",
                "Refinement.md": "# Refinement Content\n\nThis is mock generated refinement content.",
                "Completion.md": "# Completion Content\n\nThis is mock generated completion content.",
            }.get(filename, "")

            assert file_path.read_text() == expected_content, f"Unexpected content in {filename}"

# Example of modern Pydantic model with ConfigDict
from pydantic import BaseModel, ConfigDict

class TechStack(BaseModel):
    """Technology stack model."""
    framework: str
    language: str 
    features: list[str]

    model_config = ConfigDict(
        title="Technology Stack",
        extra="forbid",
        frozen=True
    )

# Example of modern importlib.resources usage
from importlib import resources
from pathlib import Path

def read_tokenizer() -> str:
    """Read tokenizer data using modern importlib.resources."""
    tokenizer_path: Path = resources.files("litellm.llms.tokenizers").joinpath("anthropic_tokenizer.json")
    return tokenizer_path.read_text(encoding="utf-8")
