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
