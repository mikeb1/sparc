import pytest
import pytest_asyncio

# Configure pytest-asyncio
pytest.register_assert_rewrite('pytest_asyncio')
pytestmark = pytest.mark.asyncio
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path
from gui.streamlit.utils.generator import generate_sparc_content, detect_tech_stack_from_description

# Mock response for tech stack detection
MOCK_TECH_STACK_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content='{"framework": "Next.js", "language": "typescript", "features": ["authentication", "database", "api"]}'
            )
        )
    ]
)

# Mock response for content generation
MOCK_CONTENT_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content="# Generated Content\n\nThis is mock generated content."
            )
        )
    ]
)

@pytest.fixture
def mock_completion():
    with patch('gui.streamlit.utils.generator.completion') as mock:
        async def async_mock(*args, **kwargs):
            # Return tech stack response for tech stack detection
            if "Extract tech stack from" in args[0]["messages"][1]["content"]:
                return MOCK_TECH_STACK_RESPONSE
            # Return content response for file generation
            return MOCK_CONTENT_RESPONSE
        mock.side_effect = async_mock
        yield mock

@pytest.mark.asyncio
async def test_detect_tech_stack_from_description(mock_completion):
    """Test tech stack detection from project description."""
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"
    
    mock_completion.return_value = MOCK_TECH_STACK_RESPONSE
    tech_stack = await detect_tech_stack_from_description(project_desc, model)
    
    assert tech_stack["framework"] == "Next.js"
    assert tech_stack["language"] == "typescript"
    assert "authentication" in tech_stack["features"]
    assert "database" in tech_stack["features"]
    assert "api" in tech_stack["features"]

@pytest.mark.asyncio
async def test_generate_sparc_content(mock_completion):
    """Test SPARC content generation."""
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"
    
    mock_completion.return_value = MOCK_CONTENT_RESPONSE
    files_content = await generate_sparc_content(project_desc, model)
    
    # Verify all expected files are generated
    expected_files = [
        "Specification.md",
        "Architecture.md",
        "Pseudocode.md",
        "Refinement.md",
        "Completion.md",
        "guidance.toml"
    ]
    
    for filename in expected_files:
        assert filename in files_content
        assert files_content[filename] is not None
        assert len(files_content[filename]) > 0

    # Verify guidance.toml contains tech stack information
    assert "Next.js" in files_content["guidance.toml"]
    assert "typescript" in files_content["guidance.toml"]

@pytest.mark.asyncio
async def test_generate_sparc_content_error_handling():
    """Test error handling in SPARC content generation."""
    with patch('gui.streamlit.utils.generator.completion', side_effect=Exception("API Error")):
        project_desc = "Build a Next.js web application with TypeScript"
        model = "claude-3-sonnet-20240229"
        
        with pytest.raises(Exception) as exc_info:
            await generate_sparc_content(project_desc, model)
        
        assert "API Error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_file_structure(mock_completion, tmp_path):
    """Test that generated files follow expected structure."""
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"
    
    mock_completion.return_value = MOCK_CONTENT_RESPONSE
    files_content = await generate_sparc_content(project_desc, model)
    
    # Write files to temporary directory
    for filename, content in files_content.items():
        file_path = tmp_path / filename
        file_path.write_text(str(content))
        
        # Verify file exists and has content
        assert file_path.exists()
        assert file_path.stat().st_size > 0
