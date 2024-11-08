#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
import asyncio
import aiohttp
from pathlib import Path
import json

from litellm import completion
from dataclasses import dataclass
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure LiteLLM to use our logger
import litellm
litellm.set_verbose = False  # Disable default logging
litellm.success_callback = []  # Disable success callbacks
litellm.logger = None  # Completely disable LiteLLM's logger

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

def _generate_component_code(component: str) -> str:
    """Generate actual implementation code for a component."""
    if component == "AuthService":
        return '''from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

class AuthService:
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return AuthService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return AuthService.pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
'''
    elif component == "UserService":
        return '''from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .databaseservice import DatabaseService, get_db
from .models import User, UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.db.delete(db_user)
        self.db.commit()
        return True
'''
    elif component == "DatabaseService":
        return '''from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
'''
    elif component == "ErrorHandler":
        return '''from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

class ErrorHandler:
    @staticmethod
    def handle_validation_error(exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )

    @staticmethod
    def handle_credentials_error() -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def handle_not_found_error() -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found"}
        )

    @staticmethod
    def handle_database_error(exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred"}
        )
'''
    return f"class {component}:\n    pass\n"

def _generate_test_code(component: str) -> str:
    """Generate test code for a component."""
    if component == "AuthService":
        return '''import pytest
from datetime import timedelta
from jose import jwt
from src.authservice import AuthService

def test_password_hashing():
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    assert AuthService.verify_password(password, hashed)
    assert not AuthService.verify_password("wrongpassword", hashed)

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = AuthService.create_access_token(data)
    payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])
    assert payload["sub"] == data["sub"]

def test_verify_token():
    data = {"sub": "test@example.com"}
    token = AuthService.create_access_token(data)
    payload = AuthService.verify_token(token)
    assert payload["sub"] == data["sub"]
'''
    elif component == "UserService":
        return '''import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.userservice import UserService
from .models import UserCreate, UserUpdate

def test_create_user(db: Session):
    service = UserService(db)
    user_data = UserCreate(email="test@example.com", password="testpass123")
    user = service.create_user(user_data)
    assert user.email == user_data.email

def test_get_user_by_email(db: Session):
    service = UserService(db)
    user = service.get_user_by_email("test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

def test_update_user(db: Session):
    service = UserService(db)
    update_data = UserUpdate(email="updated@example.com")
    updated_user = service.update_user(1, update_data)
    assert updated_user.email == update_data.email
'''
    elif component == "DatabaseService":
        return '''import pytest
from sqlalchemy.orm import Session
from src.databaseservice import get_db, init_db

def test_get_db():
    db = next(get_db())
    assert isinstance(db, Session)
    db.close()

def test_init_db():
    init_db()
    db = next(get_db())
    assert db is not None
    db.close()
'''
    elif component == "ErrorHandler":
        return '''import pytest
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from .errorhandler import ErrorHandler

def test_handle_validation_error():
    error = ValidationError.from_exception_data("test", [])
    response = ErrorHandler.handle_validation_error(error)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422

def test_handle_credentials_error():
    response = ErrorHandler.handle_credentials_error()
    assert isinstance(response, JSONResponse)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
'''
    return f"def test_{component.lower()}():\n    pass\n"

def _generate_guidance_toml(tech_stack: Dict[str, str]) -> str:
    """Generate guidance.toml content based on tech stack."""
    return f'''# SPARC Framework Guidance Configuration

[project]
framework = "{tech_stack['framework']}"
language = "{tech_stack['language']}"
features = {tech_stack['features']}

[architecture]
# Component naming conventions
component_style = "PascalCase"
test_prefix = "test_"
source_suffix = ".{tech_stack['language']}"

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

async def generate_file_content(filename: str, prompt: str, model: str, system_prompt: str) -> str:
    """Generate content for a single file asynchronously."""
    try:
        response = await completion(
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
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to generate {filename}: {str(e)}")
        raise

async def generate_sparc_content_async(project_desc: str, model: str) -> Dict[str, str]:
    """Asynchronously generate all SPARC architecture content."""
    tech_stack = _detect_tech_stack(project_desc)
    
    # Generate guidance.toml first since other files depend on it
    guidance_content = _generate_guidance_toml(tech_stack)
    
    # Define tasks for concurrent file generation
    tasks = []
    system_prompt = f"""You are a software architect. Generate detailed technical documentation.
Technology Stack:
- Framework/Runtime: {tech_stack['framework']}
- Language: {tech_stack['language']}
- Features: {', '.join(tech_stack['features'])}

Focus on best practices and patterns specific to this technology stack."""

    prompts = {
        "Specification.md": f"Generate a detailed software specification for: {project_desc}...",
        "Architecture.md": f"Generate a detailed software architecture for: {project_desc}...", 
        "Pseudocode.md": f"Generate pseudocode for key components of: {project_desc}...",
        "Refinement.md": f"Generate implementation details and refinements for: {project_desc}...",
        "Completion.md": f"Generate completion criteria and project structure for: {project_desc}..."
    }

    # Create tasks for concurrent generation
    for filename, prompt in prompts.items():
        tasks.append(generate_file_content(filename, prompt, model, system_prompt))

    # Wait for all files to be generated
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results with filenames
    files_content = {"guidance.toml": guidance_content}
    for filename, content in zip(prompts.keys(), results):
        if isinstance(content, Exception):
            logger.error(f"Failed to generate {filename}: {str(content)}")
            raise content
        files_content[filename] = content

    return files_content

def _detect_tech_stack(project_desc: str) -> Dict[str, str]:
    """Detect technology stack from project description."""
    tech_stack = {
        'framework': None,
        'language': None,
        'features': []
    }
    
    # Detect framework/runtime
    if 'flask' in project_desc.lower():
        tech_stack['framework'] = 'flask'
        tech_stack['language'] = 'python'
    elif 'deno' in project_desc.lower():
        tech_stack['framework'] = 'deno'
        tech_stack['language'] = 'typescript'
    
    # Detect features
    if 'websocket' in project_desc.lower():
        tech_stack['features'].append('websockets')
        
    return tech_stack

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Synchronous wrapper for async content generation."""
    return asyncio.run(generate_sparc_content_async(project_desc, model))

[project]
name = "supabase-devops-cli"
description = "{project_desc}"
version = "0.1.0"

[architecture]
# Component organization
component_style = "PascalCase"
test_prefix = "test_"
source_suffix = ".py"

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

    # Add tech stack context to system prompt
    system_prompt = f"""You are a software architect. Generate detailed technical documentation.
Technology Stack:
- Framework/Runtime: {tech_stack['framework']}
- Language: {tech_stack['language']}
- Features: {', '.join(tech_stack['features'])}

Focus on best practices and patterns specific to this technology stack."""
    
    prompts = {
        "Specification.md": f"Generate a detailed software specification for: {project_desc}\n\n"
                          "Include:\n"
                          "- Project Overview\n"
                          "- Core Requirements\n"
                          "- Technical Requirements\n"
                          "- Constraints and Assumptions\n"
                          "- Detailed implementation guidelines\n"
                          "- Testing requirements\n\n"
                          "Format the output in Markdown with comprehensive sections.",

        "Architecture.md": f"Generate a detailed software architecture for: {project_desc}\n\n"
                         "Include:\n"
                         "- System Components\n"
                         "- Component Interactions\n"
                         "- Data Flow\n"
                         "- Key Design Decisions\n"
                         "- Detailed Diagrams\n"
                         "- Implementation Guidelines\n\n"
                         "Format the output in Markdown with comprehensive sections.",

        "Pseudocode.md": f"Generate pseudocode for key components of: {project_desc}\n\n"
                        "Include:\n"
                        "- Core Classes/Functions\n"
                        "- Important Algorithms\n"
                        "- Data Structures\n\n"
                        "Format the output in Markdown with code blocks.",

        "Refinement.md": f"Generate implementation details and refinements for: {project_desc}\n\n"
                        "Include:\n"
                        "- Implementation Steps\n"
                        "- Error Handling\n"
                        "- Testing Strategy\n"
                        "- Performance Considerations\n\n"
                        "Format the output in Markdown with detailed sections.",

        "Completion.md": f"Generate completion criteria and project structure for: {project_desc}\n\n"
                        "Include:\n"
                        "- Project Structure\n"
                        "- Development Steps\n"
                        "- Testing Requirements\n"
                        "- Deployment Considerations\n\n"
                        "Format the output in Markdown with clear sections."
    }

    files_content = {}
    
    # Add guidance.toml to the output first
    files_content["guidance.toml"] = guidance_content.format(project_desc=project_desc)
    
    # Generate other files using the guidance
    for filename, prompt in prompts.items():
        logger.info(f"Generating {filename}...")
        try:
            logger.info(f"Requesting {filename} from {model}...")
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
            content_length = len(response.choices[0].message.content)
            logger.info(f"Generated {filename} ({content_length:,} characters)")
            files_content[filename] = response.choices[0].message.content
            logger.info(f"Successfully generated {filename}")
        except Exception as e:
            logger.error(f"Failed to generate {filename}: {str(e)}")
            raise

    return files_content

def main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')

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

    args = parser.parse_args()
    
    # Update config with selected model
    config = SPARCConfig(
        aider_model=args.model if hasattr(args, 'model') else 'claude-3-sonnet-20240229'
    )

    if args.mode == 'architect':
        try:
            # Join the project description words into a single string
            project_desc = ' '.join(args.project_description)
            logger.info(f"Architecting project: {project_desc}")
            
            # Generate content concurrently
            files_content = generate_sparc_content(project_desc, config.aider_model)
            
            # Create architecture directory with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = '-'.join(project_desc.split())[:30]
            arch_dir_name = f"architecture_{timestamp}_{base_name}"
            arch_dir = Path(arch_dir_name)
            arch_dir.mkdir(parents=True, exist_ok=True)
            
            # Save generated files
            for filename, content in files_content.items():
                file_path = arch_dir / filename
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Saved {filename} to {file_path}")
                except Exception as e:
                    logger.error(f"Failed to save {filename}: {str(e)}")
                    raise
                    
        except Exception as e:
            logger.error(f"Architecture generation failed: {str(e)}")
            sys.exit(1)
    elif args.mode == 'implement':
        # Find the most recent architecture directory
        arch_dirs = sorted([d for d in Path().glob("architecture_*") if d.is_dir()], reverse=True)
        if not arch_dirs:
            logger.error("No architecture directories found. Run architect mode first.")
            sys.exit(1)
        
        latest_arch_dir = arch_dirs[0]
        arch_file = latest_arch_dir / "Architecture.md"
        if not arch_file.exists():
            logger.error(f"Architecture.md not found in {latest_arch_dir}.")
            sys.exit(1)
        
        logger.info(f"Using architecture from: {latest_arch_dir}")

        with open(arch_file, 'r') as f:
            content = f.read()

        # Parse components
        import re
        components = re.findall(r'## Component: (\w+)', content)
        if not components:
            logger.error("No components found in Architecture.md")
            sys.exit(1)

        # Create source and test directories
        src_dir = Path("src")
        test_dir = Path("tests")
        src_dir.mkdir(exist_ok=True)
        test_dir.mkdir(exist_ok=True)

        # Generate files for each component
        for component in components:
            component_lower = component.lower()
            src_file = src_dir / f"{component_lower}.py"
            test_file = test_dir / f"test_{component_lower}.py"

            # Generate source file with actual implementation
            if not src_file.exists():
                src_content = _generate_component_code(component)
                with open(src_file, 'w') as f:
                    f.write(src_content)
                logger.info(f"Generated {src_file}")

            # Generate corresponding test file
            if not test_file.exists():
                test_content = _generate_test_code(component)
                with open(test_file, 'w') as f:
                    f.write(test_content)
                logger.info(f"Generated {test_file}")



if __name__ == "__main__":
    main()
