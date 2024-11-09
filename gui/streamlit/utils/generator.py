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

def detect_tech_stack_from_description(project_desc: str, model: str) -> Dict[str, str]:
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

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    
    # Detect tech stack from project description
    tech_stack = detect_tech_stack_from_description(project_desc, model)
    
    # System prompt with tech stack context
    system_prompt = f"""You are a software architect. Generate detailed technical documentation.
Technology Stack:
- Framework/Runtime: {tech_stack['framework']}
- Language: {tech_stack['language']}
- Features: {', '.join(tech_stack['features'])}

Focus on best practices and patterns specific to this technology stack."""

    # Define prompts for each file
    prompts = {
        "Specification.md": "Generate a detailed software specification...",
        "Architecture.md": "Generate a detailed software architecture...",
        "Pseudocode.md": "Generate pseudocode for key components...",
        "Refinement.md": "Generate implementation details and refinements...",
        "Completion.md": "Generate completion criteria and project structure..."
    }

    files_content = {}
    architecture_content = ""
    
    # Generate each file
    for filename, prompt in prompts.items():
        try:
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{prompt}\n\nProject: {project_desc}"}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content
            files_content[filename] = content
            
            if filename in ['Architecture.md', 'Specification.md']:
                architecture_content += f"\n\n# {filename}\n{content}"
                
        except Exception as e:
            logger.error(f"Failed to generate {filename}: {str(e)}")
            raise

    # Generate guidance.toml
    guidance_content = {
        "project": {
            "framework": tech_stack['framework'],
            "language": tech_stack['language'],
            "features": tech_stack['features']
        },
        "architecture": {
            "content": architecture_content
        }
    }
    
    files_content["guidance.toml"] = toml.dumps(guidance_content)
    
    return files_content

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
