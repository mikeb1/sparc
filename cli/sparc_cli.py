#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from litellm import completion

import toml  # Ensure toml is installed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    
    # LiteLLM settings
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4096
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
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def handle_not_found_error() -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found"},
        )

    @staticmethod
    def handle_database_error(exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred"},
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

def main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI with LiteLLM integration')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')

    # Common arguments for all modes
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--model', type=str,
                             default='claude-3-sonnet-20240229',
                             help='LiteLLM model to use')
    parent_parser.add_argument('--temperature', type=float,
                             default=0.7,
                             help='LiteLLM temperature parameter')
    parent_parser.add_argument('--max-tokens', type=int,
                             default=4096,
                             help='Maximum tokens for LiteLLM response')
    parent_parser.add_argument('--litellm-api-key', type=str,
                             help='API key for LiteLLM')

    # Architect mode
    parser_architect = subparsers.add_parser('architect', parents=[parent_parser], help='Run in architect mode')
    parser_architect.add_argument('project_type', nargs='?', type=str, 
                                help='Type of project to architect (e.g., fastapi, django, cli)')
    parser_architect.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')

    # Implement mode
    parser_implement = subparsers.add_parser('implement', parents=[parent_parser], help='Run in implementation mode')
    parser_implement.add_argument('--max-attempts', type=int, default=3,
                                help='Maximum attempts for implementation')
    parser_implement.add_argument('--guidance-file', type=str, default='guidance.toml',
                                help='Path to guidance TOML file')

    args = parser.parse_args()

    # Initialize config based on arguments
    config = SPARCConfig(
        aider_model=args.model if hasattr(args, 'model') else 'claude-3-sonnet-20240229',
        max_attempts=args.max_attempts if hasattr(args, 'max_attempts') else 3,
        verbose=args.verbose if hasattr(args, 'verbose') else False,
        guidance_file=args.guidance_file if hasattr(args, 'guidance_file') else 'guidance.toml'
    )

    if args.mode == 'architect':
        try:
            # Load or create guidance based on project type
            guidance = {}
            if args.project_type:
                if args.project_type.lower() == 'fastapi':
                    guidance = {
                        'specification': {
                            'content': '''Create a FastAPI REST API service with:
1. User Authentication:
   - JWT token-based authentication 
   - User registration and login endpoints
   - Password hashing with bcrypt
   - Token refresh mechanism

2. Data Models:
   - User model with email, hashed password, and profile info
   - SQLAlchemy ORM integration
   - SQLite database for storage
   - Pydantic schemas for request/response validation

3. API Features:
   - OpenAPI documentation
   - Input validation using Pydantic
   - Proper error handling with status codes
   - Rate limiting for API endpoints
   - CORS middleware configuration

4. Testing:
   - Unit tests for all endpoints
   - Integration tests with test database
   - Test fixtures and helpers
   - 100% code coverage target'''
                        }
                    }
                # Add more project types here
                logger.info(f"Using predefined guidance for {args.project_type} project")
            
            # Load custom guidance file if it exists
            if os.path.exists(config.guidance_file):
                with open(config.guidance_file, 'r') as f:
                    custom_guidance = toml.load(f)
                    guidance.update(custom_guidance)
                logger.info(f"Loaded custom guidance from {config.guidance_file}")
            elif not guidance:
                logger.warning(f"No guidance file found and no project type specified. Using default prompts.")
        except Exception as e:
            logger.warning(f"Failed to load guidance file: {e}")
            guidance = {}

        # Create architecture directory
        arch_dir = Path(config.architecture_dir)
        arch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created architecture directory at {arch_dir.resolve()}")

        # Create architecture files
        files_to_generate = [
            "Specification.md",
            "Pseudocode.md", 
            "Architecture.md",
            "Refinement.md",
            "Completion.md"
        ]

        for filename in files_to_generate:
            file_path = arch_dir / filename
            if not file_path.exists():
                content = guidance.get(filename[:-3].lower(), {}).get('content', f"# {filename[:-3]}\n")
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Generated {filename}")
            else:
                logger.info(f"{filename} already exists. Skipping.")
    
    elif args.mode == 'implement':
        # Read Architecture.md to find components
        arch_file = Path(config.architecture_dir) / "Architecture.md"
        if not arch_file.exists():
            logger.error("Architecture.md not found. Run architect mode first.")
            sys.exit(1)

        with open(arch_file, 'r') as f:
            content = f.read()

        # Parse components using regex
        import re
        components = re.findall(r'## Component: (\w+)', content)
        if not components:
            logger.error("No components found in Architecture.md")
            sys.exit(1)

        # Create source and test directories
        src_dir = Path(config.source_dir)
        test_dir = Path(config.test_dir)
        src_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)

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
            else:
                logger.info(f"{src_file} already exists. Skipping.")

            # Generate corresponding test file
            if not test_file.exists():
                test_content = _generate_test_code(component)
                with open(test_file, 'w') as f:
                    f.write(test_content)
                logger.info(f"Generated {test_file}")
            else:
                logger.info(f"{test_file} already exists. Skipping.")

        # Initialize Git repository if enabled
        if config.use_git:
            if not (Path(".git")).exists():
                logger.info("Initializing new Git repository.")
                subprocess.run(["git", "init"], check=True)
            else:
                logger.info("Git repository already initialized.")

            # Add files to Git
            subprocess.run(["git", "add", "."], check=True)
            commit_message = "Initial commit by SPARC CLI"
            if config.aider_auto_commits:
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
                logger.info("Committed initial files to Git.")

        # Optionally run tests
        if config.auto_test:
            test_cmd = config.test_cmd if config.test_cmd else "pytest"
            logger.info(f"Running tests with command: {test_cmd}")
            result = subprocess.run(test_cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("All tests passed.")
            else:
                logger.error(f"Tests failed:\n{result.stdout}\n{result.stderr}")
                if not config.dirty_commits:
                    sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
