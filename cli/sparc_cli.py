#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
import asyncio
import concurrent.futures
from typing import List, Dict
from pathlib import Path
import json
import toml
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

def _generate_guidance_toml(tech_stack: Dict[str, str], architecture_content: str = "") -> str:
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

def _detect_tech_stack(project_desc: str) -> Dict[str, str]:
    """Detect technology stack from project description."""
    tech_stack = {
        'framework': None,
        'language': None,
        'features': []
    }
    
    desc_lower = project_desc.lower()
    
    # Detect framework/runtime
    if 'nextjs' in desc_lower or 'next.js' in desc_lower:
        tech_stack['framework'] = 'nextjs'
        tech_stack['language'] = 'typescript'
    elif 'flask' in desc_lower:
        tech_stack['framework'] = 'flask'
        tech_stack['language'] = 'python'
    elif 'deno' in desc_lower:
        tech_stack['framework'] = 'deno'
        tech_stack['language'] = 'typescript'
    
    # Detect features
    features = []
    if 'websocket' in desc_lower:
        features.append('websockets')
    if 'sticky top nav' in desc_lower:
        features.append('sticky-navigation')
    if 'sidebar' in desc_lower:
        features.append('sidebar')
    if 'mobile' in desc_lower:
        features.append('mobile-responsive')
    if 'view' in desc_lower:
        features.append('view-management')
    if 'agent' in desc_lower:
        features.append('agent-management')
        
    tech_stack['features'] = features
        
    return tech_stack

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    
    tech_stack = _detect_tech_stack(project_desc)
    
    # Generate guidance.toml first
    guidance_content = """# SPARC Framework Project Configuration

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

async def async_main():
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
    parser_implement.add_argument('project_description', type=str, nargs='*',
                                help='Optional description of the project to implement')

    args = parser.parse_args()
    
    # Update config with selected model
    config = SPARCConfig(
        aider_model=args.model if hasattr(args, 'model') else 'claude-3-sonnet-20240229'
    )

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
        base_name = '-'.join(project_desc.split())[:30]  # First 30 chars, normalize spaces
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
            r'## Component: (\w+)',  # Classic component header
            r'### (\w+Component)\b',  # Component suffix pattern
            r'## (\w+Service)\b',     # Service suffix pattern
            r'## Components\s+[-*]\s*(\w+)',  # Bullet list items
            r'class (\w+):',          # Class definitions
            r'interface (\w+)\s*{',    # TypeScript interfaces
        ]
        
        components = set()
        for pattern in component_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            components.update(matches)
            
        # Filter out common words that might match but aren't components
        excluded_words = {'Component', 'Service', 'Class', 'Interface', 'Implementation'}
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

            # Use aider to generate test file first (TDD approach)
            test_prompt = f"""Create a comprehensive test file for the {component} component following TDD principles.
The component is part of a swarm agent system using LangChain.js.
Write thorough unit tests that verify all expected functionality.
Include edge cases and error conditions.
Use proper test isolation and mocking where appropriate.
The tests should guide the implementation."""

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

            # Use aider to implement the component based on the tests
            impl_prompt = f"""Implement the {component} component to pass the tests in {test_file}.
Follow best practices for TypeScript/JavaScript development.
Ensure proper error handling and type safety.
The component is part of a swarm agent system using LangChain.js.
Make the implementation clean, efficient, and well-documented."""

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
