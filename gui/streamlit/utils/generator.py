import os
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime
import toml
from litellm import completion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def detect_tech_stack_from_description(project_desc: str, model: str) -> Dict[str, str]:
    """Use LLM to detect tech stack from project description."""
    try:
        response = await completion(
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
        
        # Parse JSON response
        import json
        tech_stack = json.loads(response.choices[0].message.content)
        logger.info(f"Detected tech stack: {tech_stack}")
        return tech_stack
        
    except Exception as e:
        logger.error(f"Failed to detect tech stack: {e}")
        return {
            'framework': 'Flask',
            'language': 'python',
            'features': ['api', 'database', 'authentication']
        }

async def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    try:
        # Detect tech stack from project description
        tech_stack = await detect_tech_stack_from_description(project_desc, model)
        
        # Start with just Specification.md
        prompts = {
        "Specification.md": """Generate a detailed software specification document that includes:
1. Project Overview
2. Core Requirements
3. Technical Requirements
4. User Interface Requirements
5. Performance Requirements
6. Security Requirements
7. Testing Requirements
8. Deployment Requirements

Be specific and detailed. Format in Markdown."""
    }

        # System prompt focused on specification
        system_prompt = f"""You are a senior software architect specializing in detailed specifications.
Your task is to create a comprehensive software specification document.
Focus on clarity, completeness, and actionable requirements.

Project Context:
- Framework: {tech_stack['framework']}
- Language: {tech_stack['language']}
- Features: {', '.join(tech_stack['features'])}"""

        files_content = {}
        
        # Generate specification file first
        for filename, prompt in prompts.items():
            try:
                response = await completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{prompt}\n\nProject Description: {project_desc}"}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                files_content[filename] = content
                logger.info(f"Generated {filename} successfully")
                
            except Exception as e:
                logger.error(f"Failed to generate {filename}: {str(e)}")
                raise

        # Create minimal guidance.toml
        guidance_content = {
            "project": {
                "framework": tech_stack['framework'],
                "language": tech_stack['language'],
                "features": tech_stack['features']
            },
            "specification": {
                "content": files_content["Specification.md"]
            }
        }
        
        files_content["guidance.toml"] = toml.dumps(guidance_content)
        
        return files_content
        
    except Exception as e:
        logger.error(f"Architecture generation failed: {str(e)}")
        raise

def save_generated_content(content: Dict[str, str], output_dir: Path) -> Path:
    """Save generated content to files in the output directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_dir / f"architecture_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, content in content.items():
        file_path = output_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved {filename} ({len(content):,} chars)")
        except Exception as e:
            logger.error(f"Failed to save {filename}: {str(e)}")
            raise
            
    return output_dir
