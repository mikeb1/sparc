# gui/tests/test_generator.py

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging
import json
import toml

# Configure logging for better debugging output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the functions to be tested
from gui.streamlit.utils.generator import (
    generate_sparc_content,
    detect_tech_stack_from_description
)

# Mock responses for different completion calls
MOCK_TECH_STACK_RESPONSE = MagicMock(
    choices=[
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "framework": "Next.js",
                    "language": "typescript",
                    "features": ["authentication", "database", "api"]
                })
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

# Define additional mock responses if more files are to be generated in the future
# For now, based on the provided code, only Specification.md and guidance.toml are generated

@pytest.fixture
def mock_completion():
    """
    Fixture to mock the 'completion' function used in content generation.
    It returns different mock responses based on the content of the messages.
    """
    with patch('litellm.completion') as mock:
        async def async_mock(*args, **kwargs):
            messages = kwargs.get('messages', [])
            logger.debug(f"Mock received messages: {[msg.get('content', '') for msg in messages]}")
            # Check the messages to determine which response to return
            for msg in messages:
                content = msg.get('content', '')
                if 'Extract tech stack from:' in content:
                    logger.debug("Returning MOCK_TECH_STACK_RESPONSE")
                    return MOCK_TECH_STACK_RESPONSE
                elif 'Generate a detailed software specification document' in content:
                    logger.debug("Returning MOCK_SPECIFICATION_RESPONSE")
                    return MOCK_SPECIFICATION_RESPONSE
                # Add more conditions here if more files are generated in the future
            # Default response if no condition matches
            logger.debug("Returning default MOCK_SPECIFICATION_RESPONSE")
            return MOCK_SPECIFICATION_RESPONSE

        mock.side_effect = async_mock
        yield mock

@pytest.mark.asyncio
async def test_detect_tech_stack_from_description(mock_completion):
    """
    Test tech stack detection from project description.
    Ensures that the correct tech stack is extracted.
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
    Ensures that Specification.md and guidance.toml are generated with correct content.
    """
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"

    files_content = await generate_sparc_content(project_desc, model)

    # Define expected content for each file
    expected_files = {
        "Specification.md": "# Specification Content\n\nThis is mock generated specification content.",
    }

    # Verify that each expected file is present and has the correct content
    for filename, expected_content in expected_files.items():
        assert filename in files_content, f"Missing file: {filename}"
        actual_content = files_content[filename]
        assert actual_content == expected_content, (
            f"Unexpected content in {filename}:\n"
            f"Expected:\n{expected_content}\n"
            f"Got:\n{actual_content}"
        )
        logger.debug(f"{filename} content verified successfully.")

    # Verify 'guidance.toml' separately
    assert "guidance.toml" in files_content, "Missing file: guidance.toml"
    guidance_content = files_content["guidance.toml"]

    expected_guidance = toml.dumps({
        "project": {
            "framework": "Next.js",
            "language": "typescript",
            "features": ["authentication", "database", "api"]
        },
        "specification": {
            "content": "# Specification Content\n\nThis is mock generated specification content."
        }
    })

    assert guidance_content == expected_guidance, (
        f"Unexpected content in guidance.toml:\n"
        f"Expected:\n{expected_guidance}\n"
        f"Got:\n{guidance_content}"
    )
    logger.debug("guidance.toml content verified successfully.")

@pytest.mark.asyncio
async def test_generate_sparc_content_error_handling():
    """
    Test error handling in SPARC content generation.
    Ensures that exceptions are properly raised and handled.
    """
    with patch('litellm.completion', side_effect=Exception("API Error")):
        project_desc = "Build a Next.js web application with TypeScript"
        model = "claude-3-sonnet-20240229"

        with pytest.raises(Exception) as exc_info:
            await generate_sparc_content(project_desc, model)

        assert "API Error" in str(exc_info.value), "Exception message should contain 'API Error'"
        logger.debug("Error handling in generate_sparc_content verified successfully.")

@pytest.mark.asyncio
async def test_file_structure(mock_completion, tmp_path):
    """
    Test that generated files follow the expected structure.
    Writes files to a temporary directory and verifies their existence and content.
    """
    project_desc = "Build a Next.js web application with TypeScript"
    model = "claude-3-sonnet-20240229"

    files_content = await generate_sparc_content(project_desc, model)

    # Save the generated content to the temporary directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = tmp_path / f"architecture_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created temporary directory: {output_dir}")

    for filename, content in files_content.items():
        file_path = output_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved {filename} successfully.")
        except Exception as e:
            logger.error(f"Failed to save {filename}: {str(e)}")
            raise

        # Verify file exists
        assert file_path.exists(), f"File {filename} does not exist in the temporary directory."
        logger.debug(f"Verified existence of {filename}.")

        # Verify file is not empty
        assert file_path.stat().st_size > 0, f"File {filename} is empty."
        logger.debug(f"Verified that {filename} is not empty.")

        # Optionally, verify the content matches expected
        if filename == "guidance.toml":
            expected_content = toml.dumps({
                "project": {
                    "framework": "Next.js",
                    "language": "typescript",
                    "features": ["authentication", "database", "api"]
                },
                "specification": {
                    "content": "# Specification Content\n\nThis is mock generated specification content."
                }
            })
            assert file_path.read_text() == expected_content, f"Unexpected content in {filename}"
            logger.debug(f"Content of {filename} matches expected.")
        elif filename == "Specification.md":
            expected_content = "# Specification Content\n\nThis is mock generated specification content."
            assert file_path.read_text() == expected_content, f"Unexpected content in {filename}"
            logger.debug(f"Content of {filename} matches expected.")
        else:
            # If more files are added in the future, handle them here
            pass

# Optional: If you have Pydantic models, update them to use ConfigDict to address deprecation warnings
# Example:
# from pydantic import BaseModel, ConfigDict
#
# class MyModel(BaseModel):
#     name: str
#     value: int
#
#     model_config = ConfigDict(
#         title="My Model",
#         extra="forbid",
#     )
#
# Optional: Update deprecated 'open_text' usage in your main codebase
# Example replacement:
# from importlib import resources
#
# # Old
# # with resources.open_text("litellm.llms.tokenizers", "anthropic_tokenizer.json") as f:
# #     data = f.read()
#
# # New
# data = resources.files("litellm.llms.tokenizers").joinpath("anthropic_tokenizer.json").read_text()
