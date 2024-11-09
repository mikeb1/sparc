import pytest
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path
from gui.streamlit.utils.generator import generate_sparc_content, detect_tech_stack_from_description

# Mock response for tech stack detection
MOCK_TECH_STACK_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content='''
                {
                    "framework": "Next.js",
                    "language": "typescript",
                    "features": ["authentication", "database", "api"]
                }
                '''
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
        # Configure the mock to return different responses based on the prompt
        async def mock_completion_side_effect(*args, **kwargs):
            messages = kwargs.get('messages', [])
            if any("Extract tech stack" in msg.get('content', '') for msg in messages):
                return MOCK_TECH_STACK_RESPONSE
            return MOCK_CONTENT_RESPONSE
            
        mock.side_effect = mock_completion_side_effect
        yield mock

@pytest.mark.asyncio
async def test_detect_tech_stack_from_description(mock_completion):
    """Test tech stack detection from project description."""
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"
    
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
async def test_generate_sparc_content_error_handling(mock_completion):
    """Test error handling in SPARC content generation."""
    with patch('gui.streamlit.utils.generator.completion', side_effect=Exception("API Error")):
        project_desc = "Build a Next.js web application with TypeScript"
        model = "claude-3-sonnet-20240229"
        
        with pytest.raises(Exception) as exc_info:
            await generate_sparc_content(project_desc, model)
        
        assert "API Error" in str(exc_info.value)

def test_file_structure():
    """Test that generated files follow expected structure."""
    # Create a temporary directory for testing
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Run the async test in an event loop
        async def run_test():
            with patch('gui.streamlit.utils.generator.completion') as mock:
                mock.return_value = MOCK_CONTENT_RESPONSE
                
                project_desc = "Build a Next.js web application with TypeScript"
                model = "claude-3-sonnet-20240229"
                
                files_content = await generate_sparc_content(project_desc, model)
                
                # Write files to test directory
                for filename, content in files_content.items():
                    file_path = test_dir / filename
                    file_path.write_text(content)
                    
                    # Verify file exists and has content
                    assert file_path.exists()
                    assert file_path.stat().st_size > 0
                    
        asyncio.run(run_test())
        
    finally:
        # Cleanup test directory
        import shutil
        shutil.rmtree(test_dir)
