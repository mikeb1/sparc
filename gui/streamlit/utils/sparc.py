import os
import subprocess
import logging
from pathlib import Path
import toml
from typing import Dict, Optional
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_sparc_architect(
    project_desc: str,
    model: str = "claude-3-sonnet-20240229",
    guidance_file: Optional[str] = None
) -> Dict[str, str]:
    """Run SPARC CLI in architect mode."""
    try:
        # Build command
        cmd = ["python", "sparc_cli.py", "architect"]
        if model:
            cmd.extend(["--model", model])
        if guidance_file:
            cmd.extend(["--guidance-file", guidance_file])
        cmd.append(project_desc)

        # Run command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"SPARC architect failed: {stderr.decode()}")
            return {"error": stderr.decode()}
            
        # Parse output directory from stdout
        output = stdout.decode()
        arch_dir = None
        for line in output.split('\n'):
            if "Created architecture directory:" in line:
                arch_dir = line.split(": ")[1].strip()
                break
                
        if not arch_dir:
            return {"error": "Could not find architecture directory in output"}
            
        # Read generated files
        arch_path = Path(arch_dir)
        files = {}
        for file in arch_path.glob("*.md"):
            files[file.name] = file.read_text()
            
        if "guidance.toml" in os.listdir(arch_path):
            files["guidance.toml"] = toml.load(arch_path / "guidance.toml")
            
        return {
            "success": True,
            "arch_dir": arch_dir,
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Error running SPARC architect: {str(e)}")
        return {"error": str(e)}

async def run_sparc_implement(
    arch_dir: str,
    model: str = "claude-3-sonnet-20240229",
    max_attempts: int = 3
) -> Dict[str, str]:
    """Run SPARC CLI in implement mode."""
    try:
        # Build command
        cmd = ["python", "sparc_cli.py", "implement"]
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--max-attempts", str(max_attempts)])
        cmd.extend(["--guidance-file", str(Path(arch_dir) / "guidance.toml")])

        # Run command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"SPARC implement failed: {stderr.decode()}")
            return {"error": stderr.decode()}
            
        # Parse output directory from stdout
        output = stdout.decode()
        impl_dir = None
        for line in output.split('\n'):
            if "Created implementation directory:" in line:
                impl_dir = line.split(": ")[1].strip()
                break
                
        if not impl_dir:
            return {"error": "Could not find implementation directory in output"}
            
        # Read generated files
        impl_path = Path(impl_dir)
        files = {
            "src": {},
            "tests": {}
        }
        
        # Read source files
        src_dir = impl_path / "src"
        if src_dir.exists():
            for file in src_dir.glob("*.py"):
                files["src"][file.name] = file.read_text()
                
        # Read test files
        test_dir = impl_path / "tests"
        if test_dir.exists():
            for file in test_dir.glob("test_*.py"):
                files["tests"][file.name] = file.read_text()
                
        return {
            "success": True,
            "impl_dir": impl_dir,
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Error running SPARC implement: {str(e)}")
        return {"error": str(e)}
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import toml
from litellm import completion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_sparc_architect(project_desc: str, model: str, guidance_file: str) -> Dict:
    """Run SPARC architect mode to generate architecture files."""
    try:
        # Generate content using LiteLLM
        content = await generate_sparc_content(project_desc, model)
        
        # Create uniquely identified architecture directory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arch_dir = Path("architecture") / f"architecture_{timestamp}"
        arch_dir.mkdir(parents=True, exist_ok=True)
        
        # Save generated files
        for filename, file_content in content.items():
            file_path = arch_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            logger.info(f"Generated {filename}")
            
        return {
            "arch_dir": str(arch_dir),
            "files": content
        }
        
    except Exception as e:
        logger.error(f"Architecture generation failed: {str(e)}")
        return {"error": str(e)}

async def run_sparc_implement(arch_dir: str, model: str, max_attempts: int = 3) -> Dict:
    """Run SPARC implement mode to develop components."""
    try:
        arch_path = Path(arch_dir)
        if not arch_path.exists():
            raise FileNotFoundError(f"Architecture directory not found: {arch_dir}")
            
        # Create implementation directories
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        impl_dir = Path("implementation") / f"implementation_{timestamp}"
        src_dir = impl_dir / "src"
        test_dir = impl_dir / "tests"
        
        src_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Read architecture files
        arch_file = arch_path / "Architecture.md"
        if not arch_file.exists():
            raise FileNotFoundError("Architecture.md not found")
            
        arch_content = arch_file.read_text()
        
        # Extract components
        import re
        components = re.findall(r'## Component: (\w+)', arch_content)
        
        if not components:
            raise ValueError("No components found in Architecture.md")
            
        # Generate code for each component
        files = {"src": {}, "tests": {}}
        
        for component in components:
            # Generate test file
            test_content = await generate_test_code(component, model)
            test_file = f"test_{component.lower()}.py"
            files["tests"][test_file] = test_content
            
            with open(test_dir / test_file, 'w') as f:
                f.write(test_content)
                
            # Generate implementation
            impl_content = await generate_implementation(component, model)
            impl_file = f"{component.lower()}.py"
            files["src"][impl_file] = impl_content
            
            with open(src_dir / impl_file, 'w') as f:
                f.write(impl_content)
                
        return {
            "impl_dir": str(impl_dir),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Implementation failed: {str(e)}")
        return {"error": str(e)}

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    try:
        # Detect tech stack
        tech_stack = detect_tech_stack(project_desc, model)
        
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
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{prompt}\n\nProject: {project_desc}"}
                ],
                temperature=0.7,
                api_key=os.getenv('ANTHROPIC_API_KEY')  # Explicitly pass API key
            )
            content = response.choices[0].message.content
            files_content[filename] = content
            
            if filename in ['Architecture.md', 'Specification.md']:
                architecture_content += f"\n\n# {filename}\n{content}"

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
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise

def detect_tech_stack(project_desc: str, model: str) -> Dict[str, str]:
    """Detect technology stack from project description."""
    try:
        response = completion(
            model=model,
            messages=[{
                "role": "system",
                "content": """You are a technical analyst. Extract the technology stack from the project description.
            }],
            temperature=0.1,
            api_key=os.getenv('ANTHROPIC_API_KEY')  # Explicitly pass API key
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
        
        import json
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Tech stack detection failed: {str(e)}")
        return {
            'framework': 'Flask',
            'language': 'python',
            'features': ['api', 'database', 'authentication']
        }

async def generate_test_code(component: str, model: str) -> str:
    """Generate test code for a component."""
    try:
        response = await completion(
            model=model,
            messages=[{
                "role": "system",
                "content": "You are a test engineer. Generate pytest test code."
            },
            {
                "role": "user",
                "content": f"Generate comprehensive pytest tests for the {component} component."
            }],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Test generation failed: {str(e)}")
        raise

async def generate_implementation(component: str, model: str) -> str:
    """Generate implementation code for a component."""
    try:
        response = await completion(
            model=model,
            messages=[{
                "role": "system",
                "content": "You are a software engineer. Generate implementation code."
            },
            {
                "role": "user",
                "content": f"Generate implementation code for the {component} component."
            }],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Implementation generation failed: {str(e)}")
        raise
