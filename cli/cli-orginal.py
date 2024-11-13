#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
import asyncio
import concurrent.futures
import re
from typing import List, Dict
from pathlib import Path
import json
import toml

from litellm import completion
from dataclasses import dataclass
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure LiteLLM and tqdm
import litellm
from tqdm import tqdm
litellm.set_verbose = False
litellm.success_callback = []
litellm.logger = None

@dataclass
class SPARCConfig:
    """Configuration class for SPARC CLI."""
    # Core directories
    architecture_dir: str = "architecture"
    test_dir: str = "tests" 
    source_dir: str = "src"
    
    # Development settings
    max_attempts: int = 3
    verbose: bool = False
    guidance_file: str = "guidance.toml"
    
    # Model settings
    model: str = "claude-3-sonnet-20240229"  # Default to Claude 3 Sonnet
    temperature: float = 0.7
    max_tokens: int = 4000
    litellm_api_key: Optional[str] = None
    
    # Git settings
    use_git: bool = True
    auto_commits: bool = True
    dirty_commits: bool = True
    
    # Testing settings
    auto_test: bool = False
    test_cmd: Optional[str] = None
    
    # Output settings
    pretty: bool = True
    stream: bool = True
    
    # Aider settings
    aider_model: str = "claude-3-sonnet-20240229"  # Default to Claude 3.5 Sonnet
    aider_edit_format: str = "diff"
    aider_stream: bool = True
    aider_auto_commits: bool = True

import re

def _generate_component_code(config, component: str) -> str:
    """Generate implementation code for a component based on architecture specs."""
    # Read the architecture files to determine the implementation details
    arch_dir = Path(config.architecture_dir)
    arch_file = arch_dir / "Architecture.md"
    
    if not arch_file.exists():
        logger.error("Architecture.md not found")
        return ""
        
    # Parse the architecture file to find the component specification
    arch_content = arch_file.read_text()
    component_spec = ""
    
    # Find the component's specification section
    import re
    pattern = rf"## Component: {component}\s+(.*?)(?=\n## |$)"
    match = re.search(pattern, arch_content, re.DOTALL)
    
    if match:
        component_spec = match.group(1).strip()
    else:
        logger.error(f"No specification found for component {component}")
        return ""

    # Generate code based on the architecture specification
    return component_spec

def _generate_test_code(config, component: str) -> str:
    """Generate test code based on architecture specs."""
    # Read the architecture files to determine the implementation details
    arch_dir = Path(config.architecture_dir)
    arch_file = arch_dir / "Architecture.md"
    
    if not arch_file.exists():
        logger.error("Architecture.md not found")
        return ""

    # Parse test requirements from architecture
    arch_content = arch_file.read_text()
    test_spec = ""
    
    pattern = rf"### Testing: {component}\s+(.*?)(?=\n### |$)"
    match = re.search(pattern, arch_content, re.DOTALL)
    
    if match:
        test_spec = match.group(1).strip()
    else:
        logger.warning(f"No test specification found for component {component}")
        return ""

    return test_spec

def _generate_guidance_toml(tech_stack: Dict[str, str], architecture_content: str = "") -> str:
    """Generate guidance.toml content based on tech stack."""
    # Default to python if no language detected
    language = tech_stack.get('language') or 'python'
    return f'''# SPARC Framework Guidance Configuration

[project]
framework = "{tech_stack['framework']}"
language = "{language}"
features = {tech_stack['features']}

[architecture]
# Component naming conventions
component_style = "PascalCase"
test_prefix = "test_"
source_suffix = ".{language}"
content = """
{architecture_content}
"""

# Directory structure
src_dir = "src"
test_dir = "tests"
docs_dir = "docs"

[implementation]
# Code generation settings
max_attempts = 3
test_first = true
type_hints = true

# Documentation requirements
require_docstrings = true
doc_style = "Google"

[testing]
# Testing requirements
min_coverage = 80
unit_test_required = true
integration_test_required = true

[quality]
# Code quality requirements
max_complexity = 10
max_line_length = 100
require_type_hints = true

[security]
# Security requirements
require_input_validation = true
require_authentication = true
require_authorization = true

[performance]
# Performance requirements
max_response_time_ms = 500
max_memory_usage_mb = 512
enable_caching = true

[deployment]
# Deployment requirements
containerize = true
ci_cd_required = true
monitoring_required = true

[documentation]
# Documentation requirements
readme_required = true
api_docs_required = true
architecture_docs_required = true
'''

def _detect_tech_stack(guidance_file: Path) -> Dict[str, str]:
    """Read the tech stack from guidance.toml."""
    try:
        with open(guidance_file, 'r') as f:
            guidance = toml.load(f)
            
        project = guidance.get('project', {})
        return {
            'framework': project.get('framework', ''),
            'language': project.get('language', ''),
            'features': project.get('features', [])
        }
    except Exception as e:
        logger.error(f"Failed to read tech stack from guidance.toml: {e}")
        return {}

def _detect_tech_stack_from_description(project_desc: str, model: str) -> Dict[str, str]:
    """Use LLM to detect tech stack from project description."""
    try:
        response = completion(
            model=model,
            messages=[{
                "role": "system",
                "content": """You are a technical analyst. Extract the technology stack from the project description.
Return only a JSON object with these fields:
{
    "framework": "name of the framework",
    "language": "primary programming language",
    "features": ["list", "of", "features"]
}"""
            },
            {
                "role": "user",
                "content": f"Extract tech stack from: {project_desc}"
            }],
            temperature=0.1
        )
        
        # Parse JSON response, handling potential non-JSON responses
        try:
            content = response.choices[0].message.content.strip()
            # Try to find JSON object if response contains other text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            import json
            tech_stack = json.loads(content)
            logger.info(f"Detected tech stack: {tech_stack}")
            return tech_stack
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse tech stack JSON: {e}")
            # Extract tech stack using regex fallback
            framework_match = re.search(r'"framework":\s*"([^"]+)"', content)
            language_match = re.search(r'"language":\s*"([^"]+)"', content)
            features_match = re.search(r'"features":\s*\[(.*?)\]', content, re.DOTALL)
            
            tech_stack = {
                'framework': framework_match.group(1) if framework_match else 'SPARC',
                'language': language_match.group(1) if language_match else 'python',
                'features': [f.strip(' "\'') for f in features_match.group(1).split(',')] if features_match else []
            }
            logger.info(f"Extracted tech stack using regex: {tech_stack}")
            return tech_stack
            
    except Exception as e:
        logger.error(f"Failed to detect tech stack: {e}")
        # Fallback to defaults
        return {
            'framework': 'SPARC',
            'language': 'python',
            'features': ['agent-management', 'test-driven-development']
        }

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    
    # Read any imported markdown files first
    arch_dir = Path("architecture")
    imported_files = {}
    project_context = ""
    
    if arch_dir.exists():
        for md_file in arch_dir.glob("*.md"):
            try:
                with open(md_file, 'r') as f:
                    content = f.read()
                    imported_files[md_file.name] = content
                    project_context += f"\n\n# Content from {md_file.name}\n{content}"
                    # If this is the first file, use its content to enhance project description
                    if not project_desc or project_desc == "A software project following SPARC framework principles.":
                        # Extract first meaningful paragraph
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                        if paragraphs:
                            project_desc = paragraphs[0]
            except Exception as e:
                logger.error(f"Failed to read imported file {md_file}: {str(e)}")

    # Detect tech stack from project description and imported content
    tech_stack = _detect_tech_stack_from_description(
        f"{project_desc}\n\nImported Content:\n{project_context}", 
        model
    )
    
    # Generate guidance.toml with detected tech stack
    # Default to python if no language detected
    language = tech_stack.get('language') or 'python'
    guidance_content = f"""# SPARC Framework Project Configuration

[project]
name = "{tech_stack['framework'].lower()}-agent-management"
description = "{project_desc}"
version = "0.1.0"
framework = "{tech_stack['framework']}"
language = "{language}"
features = {tech_stack['features']}

[architecture]
# Component organization
component_style = "PascalCase"
test_prefix = "test_"
source_suffix = ".{language}"

# Directory structure
src_dir = "src"
test_dir = "tests"
docs_dir = "docs"

[implementation]
# Code generation settings
max_attempts = 3
test_first = true
type_hints = true
docstring_style = "Google"

[testing]
# Testing requirements
min_coverage = 85
unit_test_required = true
integration_test_required = true

[quality]
# Code quality requirements
max_complexity = 8
max_line_length = 88
require_type_hints = true
require_docstrings = true

[security]
# Security requirements
require_input_validation = true
require_authentication = true
require_authorization = true

[deployment]
# Deployment configuration
containerize = true
ci_cd_required = true
monitoring_required = true
required_platforms = ["linux"]

[documentation]
# Documentation requirements
readme_required = true
api_docs_required = true
architecture_docs_required = true
changelog_required = true"""

    # Add tech stack context and imported content to system prompt
    system_prompt = f"""You are a software architect tasked with creating SPARC framework documentation.
Your task is to analyze the following imported content and create comprehensive SPARC architecture files
that align with and expand upon the existing project documentation.

Imported Project Context:
{project_context}

Key Instructions:
1. Maintain consistency with the imported content
2. Preserve any specific technical decisions or approaches mentioned
3. Expand and structure the content to fit SPARC framework requirements
4. Add any missing architectural details while staying true to the original vision
5. Ensure all generated content aligns with and builds upon the imported documentation

Project Description: {project_desc}

Technology Stack:
- Framework/Runtime: {tech_stack['framework']}
- Language: {tech_stack['language']}
- Features: {', '.join(tech_stack['features'])}"""
    
    prompts = {
        "Specification.md": f"""Generate a detailed software specification for: {project_desc}
Include:
- Project Overview
- Core Requirements
- Technical Requirements
- Constraints and Assumptions
- This specification should be detailed and comprehensive and used to guide development and testing.
- Be verbose and complete. 


# Specification

## Objective
Develop a comprehensive specification document for the project.

## Research and Analysis
- Use tools like Perplexity to gather information on various approaches, architectures, and relevant technical papers.
- Document findings in markdown files, including pros and cons of different approaches.

## Project Overview
- Elaborate on the project goal, providing context and background.
- Describe the target audience and their needs, including demographics and user personas.

## Functional Requirements
- List and describe each functional requirement.
- Break down complex features into smaller, manageable components.

## Non-Functional Requirements
- Detail each non-functional requirement, explaining its importance.
- Include performance metrics, security standards, and scalability considerations.

## User Scenarios and User Flows
- Describe typical user scenarios and provide user flow diagrams.
- Include step-by-step interactions and decision points.

## UI/UX Considerations
- Discuss UI/UX guidelines and include design sketches if applicable.
- Reference design principles and accessibility standards.

## File Structure Proposal
- Suggest an organized file and directory structure.
- Use markdown files to outline and guide the process.

## Assumptions
- List assumptions made during the specification process.
- Justify each assumption and its impact on the project.

## Reflection
- Justify the inclusion of each requirement.
- Consider potential challenges and propose mitigation strategies.
- Reflect on how each element contributes to the overall project goals.

Format in Markdown.""",

        "Architecture.md": f'''Generate a detailed software architecture for: {project_desc}
Include:
- System Components
- Component Interactions
- Data Flow
- Key Design Decisions
- Detailed Diagrams (if applicable) 
- File and folder structure with a brief description of each component.
- Be verbose and complete.


# Architecture

## System Components
- Core services
- Data layer
- External integrations

## Component Interactions
- Service communication
- Data flow
- API contracts

## Data Flow
- Input processing
- Data transformation
- Storage patterns

## Key Design Decisions
- Technology choices
- Architectural patterns
- Security measures
''',

        "Pseudocode.md": f'''Generate pseudocode for key components of: {project_desc}
Include:
- Core Classes/Functions
- Important Algorithms
- Data Structures
- Be compelete and verbose.
- Output using mark down and be sure to include all necessary details.
- This will be used to guide the implementation process.
- Include inlined comments to explain the logic and flow of the code.

# Pseudocode

## Core Classes/Functions
```pseudo
class MainComponent:
    def initialize():
        // Setup core dependencies
    
    def process():
        // Main processing logic
```

## Important Algorithms
```pseudo
function processData(input):
    // Data processing steps
    return result
```

## Data Structures
```pseudo
struct DataModel:
    id: string
    data: map<string, any>
    metadata: object
```
''',

        "Refinement.md": f'''Generate implementation details and refinements for: {project_desc}
Include:
- Implementation Steps
- Error Handling
- Testing Strategy
- Performance Considerations

# Refinement

## Implementation Steps
1. Environment setup
2. Core services
3. Data layer
4. API endpoints
5. Testing

## Error Handling
- Validation
- Authentication
- Database errors
- Global handlers

## Testing Strategy
- Unit tests
- Integration tests
- Performance tests
- Security tests

## Performance
- Query optimization
- Caching strategy
- Resource management
- Monitoring
''',

        "Completion.md": f'''Generate completion criteria and project structure for: {project_desc}
Include:
- Project Structure
- Development Steps
- Testing Requirements
- Deployment Considerations

# Completion Criteria

## Project Structure
- Source code organization
- Configuration files
- Documentation
- Test suite

## Development Steps
1. Environment setup
2. Core implementation
3. Testing
4. Documentation
5. Deployment preparation

## Testing Requirements
- Unit tests
- Integration tests
- Performance tests
- Security tests

## Deployment Considerations
- Environment configuration
- Dependencies
- Monitoring
- Maintenance

## Final Checklist
- All tests passing
- Documentation complete
- Security review done
- Performance benchmarks met
'''
    }

    files_content = {}
    
    # Generate architecture content first
    architecture_content = ""
    
    # Generate files using the guidance
    with tqdm(prompts.items(), desc="Generating files") as pbar:
        for filename, prompt in pbar:
            pbar.set_description(f"Generating {filename}")
            try:
                response = completion(
                    model=model,
                    messages=[{
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                content_length = len(content)
                files_content[filename] = content
                if filename in ['Architecture.md', 'Specification.md']:
                    architecture_content += f"\n\n# {filename}\n{content}"
                pbar.set_postfix(chars=f"{content_length:,}")
            except Exception as e:
                logger.error(f"Failed to generate {filename}: {str(e)}")
                raise

    # Generate guidance.toml with architecture content
    files_content["guidance.toml"] = _generate_guidance_toml(tech_stack, architecture_content)
    
    return files_content

def _import_markdown_files(import_path: str, arch_dir: Path, output_dir: Optional[Path] = None, force: bool = False) -> None:
    """Import markdown files from specified path into architecture directory.
    
    Args:
        import_path: Path to directory containing markdown files to import
        arch_dir: Target architecture directory path
        force: If True, overwrite existing files
    """
    import_path = Path(import_path)
    if not import_path.exists():
        logger.error(f"Import path '{import_path}' does not exist.")
        return

    # Create architecture directory if it doesn't exist
    arch_dir.mkdir(parents=True, exist_ok=True)

    # Track import statistics
    imported = []
    skipped = []
    failed = []

    # Find and copy all .md files
    for md_file in import_path.glob('*.md'):
        target_file = arch_dir / md_file.name
        try:
            if target_file.exists():
                if force:
                    logger.warning(f"Overwriting existing file {target_file.name}")
                    import shutil
                    shutil.copy2(md_file, target_file)
                    imported.append(md_file.name)
                else:
                    logger.warning(f"Skipping {target_file.name} - already exists in {arch_dir}")
                    skipped.append(md_file.name)
                    continue
            else:
                import shutil
                shutil.copy2(md_file, target_file)
                imported.append(md_file.name)
                logger.info(f"Imported {md_file.name} to architecture directory")
        except Exception as e:
            logger.error(f"Failed to import {md_file.name}: {str(e)}")
            failed.append(md_file.name)

    # Print summary
    if imported:
        logger.info(f"Successfully imported: {', '.join(imported)}")
    if skipped:
        logger.warning(f"Skipped existing files: {', '.join(skipped)}")
        logger.info("Use --force to overwrite existing files")
    if failed:
        logger.error(f"Failed to import: {', '.join(failed)}")

    # Print next steps
    if imported or (not imported and not failed and skipped):
        logger.info("Import completed. Use 'architect' or 'implement' mode to continue development.")
    elif failed:
        logger.error("Import failed. Please check errors above and try again.")

async def async_main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')
    
    # Add import-docs as a global argument before subparsers
    parser.add_argument('--import-docs', type=str, help='Path to import .md documentation files from')
    parser.add_argument('--force', action='store_true', help='Force overwrite of existing files during import')

    # Common arguments for all modes
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--model', type=str,
                             choices=['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'gpt-4', 'gpt-4-turbo'],
                             default='claude-3-sonnet-20240229',
                             help='AI model to use (default: claude-3-sonnet-20240229)')

    # Architect mode
    parser_architect = subparsers.add_parser('architect', parents=[parent_parser], help='Run in architect mode')
    parser_architect.add_argument('project_description', type=str, nargs='+', 
                                help='Description of the project to architect')
    parser_architect.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')

    # Implement mode
    parser_implement = subparsers.add_parser('implement', parents=[parent_parser], help='Run in implementation mode')
    parser_implement.add_argument('--max-attempts', type=int, default=3,
                                help='Maximum attempts for implementation')
    parser_implement.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')
    parser_implement.add_argument('project_description', type=str, nargs='*',
                                help='Optional description of the project to implement')

    args = parser.parse_args()
    
    # Update config with selected model
    config = SPARCConfig(
        aider_model=args.model if hasattr(args, 'model') else 'claude-3-sonnet-20240229'
    )

    # Handle imports first
    if args.import_docs:
        # Create base architecture directory if it doesn't exist
        base_arch_dir = Path("architecture")
        base_arch_dir.mkdir(exist_ok=True)
        
        # Create uniquely identified output directory under architecture/
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import_path = Path(args.import_docs)
        base_name = import_path.name  # Get the name of the imported directory
        output_dir_name = f"architecture_{timestamp}_{base_name}"
        output_dir = base_arch_dir / output_dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

        # Create architecture subdirectory for imported files
        arch_output_dir = output_dir / "architecture"
        arch_output_dir.mkdir(parents=True, exist_ok=True)

        # Import files to the new architecture subdirectory
        _import_markdown_files(args.import_docs, arch_output_dir, None, args.force)
        
        # If no mode specified, run architect mode with imported files as base
        if not args.mode:
            logger.info("No mode specified. Running architect mode with imported files as base...")
            
            # Create uniquely identified output directory
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            import_path = Path(args.import_docs)
            base_name = import_path.name  # Get the name of the imported directory
            output_dir_name = f"sparc_output_{timestamp}_{base_name}"
            output_dir = Path(output_dir_name)
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {output_dir_name}")

            # Copy imported files to new directory
            arch_output_dir = output_dir / "architecture"
            arch_output_dir.mkdir(parents=True, exist_ok=True)
            import shutil
            for file in arch_output_dir.glob("*.md"):
                shutil.copy2(file, arch_output_dir / file.name)
            
            # Read existing architecture files to create project description
            arch_files = {}
            for filename in ['Specification.md', 'Architecture.md']:
                file_path = arch_output_dir / filename
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        arch_files[filename] = f.read()

            # Extract project description from existing files
            project_desc = ""
            if 'Specification.md' in arch_files:
                # Try to extract first paragraph after "## Objective" or first non-empty paragraph
                content = arch_files['Specification.md']
                # Look for objective section
                import re
                objective_match = re.search(r'## Objective\s+(.+?)(?=\n\n|\Z)', content, re.DOTALL)
                if objective_match:
                    project_desc = objective_match.group(1).strip()
                else:
                    # Fall back to first non-empty paragraph
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                    if paragraphs:
                        project_desc = paragraphs[0]

            # Use default if no description found
            if not project_desc:
                project_desc = "A software project following SPARC framework principles."
            
            logger.info(f"Using project description from existing files: {project_desc}")
            
            # Generate content for missing files
            files_content = generate_sparc_content(project_desc, config.model)
            
            # Write files to the new output directory
            for filename, content in files_content.items():
                file_path = arch_output_dir / filename  # Use arch_output_dir instead of arch_dir
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Generated missing file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to save {filename}: {str(e)}")
            
            logger.info(f"\nAll files generated in: {output_dir}")
            return

    if args.mode == 'architect':
        # Join the project description words into a single string
        project_desc = ' '.join(args.project_description)
        logger.info(f"Architecting project: {project_desc}")
        
        try:
            import toml
            if os.path.exists(args.guidance_file):
                with open(args.guidance_file, 'r') as f:
                    guidance = toml.load(f)
            else:
                guidance = {}
        except Exception as e:
            logger.warning(f"Failed to load guidance file: {e}")
            guidance = {}
        # Create uniquely identified architecture directory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = '-'.join(args.project_description)[:30]  # First 30 chars, normalize spaces
        arch_dir_name = f"architecture_{timestamp}_{base_name}"
        arch_dir = Path(arch_dir_name)
        arch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created architecture directory: {arch_dir_name}")

        # Generate architecture files using LiteLLM
        files_content = generate_sparc_content(project_desc, config.aider_model)
        
        # Save the generated content
        for filename, content in files_content.items():
            file_path = arch_dir / filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Saved {filename} ({len(content):,} chars) to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save {filename}: {str(e)}")
                raise
                
        # Print summary
        logger.info("\nGenerated files summary:")
        for filename, content in files_content.items():
            logger.info(f"- {filename}: {len(content):,} characters")
    elif args.mode == 'implement':
        # Handle both absolute and relative paths for guidance file
        guidance_path = Path(args.guidance_file)
        if not guidance_path.is_absolute():
            guidance_path = Path.cwd() / guidance_path
        
        guidance_dir = guidance_path.parent
        if not guidance_dir.exists():
            logger.error(f"Directory containing guidance file '{guidance_path}' not found.")
            sys.exit(1)
            
        # Parse architecture content directly from guidance.toml
        try:
            import toml
            with open(guidance_path, 'r') as f:
                guidance_data = toml.load(f)
                architecture_content = guidance_data.get('architecture', {}).get('content', '')
                if not architecture_content:
                    logger.error("No architecture content found in guidance.toml")
                    sys.exit(1)
                logger.info("Successfully loaded architecture content from guidance.toml")
        except Exception as e:
            logger.error(f"Failed to read architecture content from guidance.toml: {str(e)}")
            sys.exit(1)

        # Create uniquely identified implementation directory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = guidance_dir.name
        impl_dir_name = f"implementation_{timestamp}_{base_name}"
        impl_dir = Path(impl_dir_name)
        impl_dir.mkdir(parents=True, exist_ok=True)
        
        # Create src and tests directories inside implementation directory
        src_dir = impl_dir / "src"
        test_dir = impl_dir / "tests"
        src_dir.mkdir(exist_ok=True)
        test_dir.mkdir(exist_ok=True)
        
        logger.info(f"Created implementation directory: {impl_dir_name}")
        logger.info(f"Using architecture from: {guidance_dir}")

        content = architecture_content

        # Parse components from architecture content
        import re
        
        # Look for component patterns in different sections
        component_patterns = [
            r'## Component: (\w+)',            # Classic component header
            r'### (\w+Component)\b',           # Component suffix pattern
            r'### (\w+Service)\b',             # Service suffix pattern
            r'### (\w+)\b',                    # Any ### header
            r'## (\w+Service)\b',              # Service in ## header
            r'## (\w+Component)\b',            # Component in ## header
            r'## Components\s+[-*]\s*(\w+)',   # Bullet list items
            r'[-*]\s*(\w+(?:Component|Service))\b',  # Bullet points with suffix
            r'[-*]\s*(\w+)\b(?:\s*-[^\n]+)?',  # Any bullet point with optional description
            r'class (\w+)[\s:{]',              # Class definitions (more flexible)
            r'interface (\w+)\s*[:{]',         # TypeScript interfaces (more flexible)
            r'\b((?:[A-Z][a-z0-9]+){2,})\b',   # PascalCase words (2+ parts)
        ]
        
        components = set()
        for pattern in component_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            components.update(matches)
            
        # Filter out common words that might match but aren't components
        excluded_words = {
            'Component', 'Service', 'Class', 'Interface', 'Implementation',
            'React', 'Next', 'JavaScript', 'TypeScript', 'Node', 'Express',
            'Frontend', 'Backend', 'Database', 'System', 'Module', 'Function',
            'Architecture', 'Design', 'Pattern', 'Testing', 'Documentation'
        }
        components = {c for c in components if c not in excluded_words}
        
        if not components:
            logger.error("No components found in architecture content")
            logger.info("Please ensure your architecture documentation defines components using one of these patterns:")
            logger.info("- ## Component: ComponentName")
            logger.info("- ### ComponentName")
            logger.info("- ## ComponentNameService")
            logger.info("- ## Components\\n- ComponentName")
            logger.info("- class ComponentName:")
            logger.info("- interface ComponentName {")
            sys.exit(1)
            
        logger.info(f"Found components: {', '.join(sorted(components))}")

        # Use the previously created directories in impl_dir
        src_dir = impl_dir / "src"
        test_dir = impl_dir / "tests"

        # Generate files for each component
        for component in components:
            component_lower = component.lower()
            src_file = src_dir / f"{component_lower}.py"
            test_file = test_dir / f"test_{component_lower}.py"

            # Get tech stack from guidance file
            tech_stack = _detect_tech_stack(Path(args.guidance_file))
            
            if not tech_stack:
                logger.error("Could not determine project technology stack")
                sys.exit(1)
                
            logger.info(f"Implementing component using: {tech_stack['framework']} with {tech_stack['language']}")
            
            # Set file extensions based on language
            file_ext = {
                'typescript': '.ts',
                'javascript': '.js', 
                'rust': '.rs'
            }.get(tech_stack['language'].lower(), '.js')
            
            test_ext = {
                'typescript': '.test.ts',
                'javascript': '.test.js',
                'rust': '_test.rs'
            }.get(tech_stack['language'].lower(), '.test.js')
            
            # Update file paths with correct extensions
            component_lower = component.lower()
            src_file = src_dir / f"{component_lower}{file_ext}"
            test_file = test_dir / f"{component_lower}{test_ext}"

            # Generate test file using appropriate testing framework
            test_prompt = f"""Create tests for the {component} component using appropriate testing frameworks for {tech_stack['framework']}.
For example:
- JavaScript/TypeScript: Jest
- Rust: built-in testing framework
Follow testing best practices for {tech_stack['language']}.
Write thorough unit tests that verify all expected functionality.
Include edge cases and error conditions.
Use proper test isolation and mocking where appropriate."""

            logger.info(f"\n{'='*80}")
            logger.info(f"Generating tests for {component} using aider...")
            logger.info(f"{'='*80}\n")
            
            # Run aider with timeout
            try:
                process = subprocess.run(
                    [
                        "aider",
                        "--yes",  # Auto-confirm prompts
                        "--model", "claude-3-sonnet-20240229",
                        "--edit-format", "diff",
                        "--message", test_prompt,
                        str(test_file)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    check=False  # Don't raise on non-zero exit
                )

                # Log output regardless of success/failure
                if process.stdout:
                    for line in process.stdout.splitlines():
                        logger.info(f"aider: {line.strip()}")
                if process.stderr:
                    for line in process.stderr.splitlines():
                        logger.error(f"aider error: {line.strip()}")
                        
                if process.returncode != 0:
                    logger.error(f"aider failed with return code {process.returncode}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error("aider process timed out after 5 minutes")
                return False
            except Exception as e:
                logger.error(f"aider process failed: {str(e)}")
                return False

            if process.returncode != 0:  # Check returncode of CompletedProcess
                logger.error(f"Failed to generate tests for {component}")
                continue
            
            logger.info(f"Generated tests at {test_file}")

            # Generate implementation using correct language/framework
            impl_prompt = f"""Implement the {component} component using {tech_stack['framework']} and {tech_stack['language']}.
Follow best practices for {tech_stack['language']} development.
Ensure proper error handling and type safety.
The component should pass the tests in {test_file}.
Make the implementation clean, efficient, and well-documented.
Use appropriate patterns and practices for {tech_stack['framework']}."""

            logger.info(f"\n{'='*80}")
            logger.info(f"Implementing {component} using aider...")
            logger.info(f"{'='*80}\n")
            
            # Run aider with timeout
            try:
                process = subprocess.run(
                    [
                        "aider",
                        "--yes",  # Auto-confirm prompts
                        "--model", "claude-3-sonnet-20240229",
                        "--edit-format", "diff",
                        "--message", impl_prompt,
                        str(src_file)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    check=False  # Don't raise on non-zero exit
                )

                # Log output regardless of success/failure
                if process.stdout:
                    for line in process.stdout.splitlines():
                        logger.info(f"aider: {line.strip()}")
                if process.stderr:
                    for line in process.stderr.splitlines():
                        logger.error(f"aider error: {line.strip()}")
                        
                if process.returncode != 0:
                    logger.error(f"aider failed with return code {process.returncode}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error("aider process timed out after 5 minutes")
                return False
            except Exception as e:
                logger.error(f"aider process failed: {str(e)}")
                return False

            if process.returncode != 0:  # Check returncode of CompletedProcess
                logger.error(f"Failed to implement {component}")
                continue
                
            logger.info(f"Generated implementation at {src_file}")

            # 4. Run tests with visual feedback
            logger.info(f"\n{'='*80}")
            logger.info(f"Running tests for {component}")
            logger.info(f"{'='*80}")

            logger.info("\nFinal implementation:")
            logger.info(f"\n{'-'*40}\n{src_file.read_text()}\n{'-'*40}")

            logger.info("\nExecuting tests...")
            try:
                test_run = subprocess.run(
                    [
                        "pytest",
                        "-v",
                        "--capture=no",  # Show test output in real-time
                        str(test_file)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=60  # 1 minute timeout for tests
                )

                # Log test output
                if test_run.stdout:
                    logger.info(f"Test output:\n{test_run.stdout}")
                if test_run.stderr:
                    logger.error(f"Test errors:\n{test_run.stderr}")

                if test_run.returncode != 0:
                    logger.error(f"Tests failed for {component}")
                    continue
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Tests timed out for {component}")
                continue
            except Exception as e:
                logger.error(f"Test execution failed: {str(e)}")
                continue
                
            logger.info(f"Tests passed for {component}")



def main():
    """Synchronous wrapper for async_main()"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
