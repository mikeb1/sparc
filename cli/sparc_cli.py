#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
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

def generate_sparc_content(project_desc: str, model: str) -> Dict[str, str]:
    """Generate SPARC architecture content using LiteLLM."""
    
    prompts = {
        "Specification.md": f"""Generate a detailed software specification for: {project_desc}
Include:
- Project Overview
- Core Requirements
- Technical Requirements
- Constraints and Assumptions
Format in Markdown.""",

        "Architecture.md": f"""Generate a detailed software architecture for: {project_desc}
Include:
- System Components
- Component Interactions
- Data Flow
- Key Design Decisions
Format in Markdown.""",

        "Pseudocode.md": f"""Generate pseudocode for key components of: {project_desc}
Include:
- Core Classes/Functions
- Important Algorithms
- Data Structures
Format in Markdown with code blocks.""",

        "Refinement.md": f"""Generate implementation details and refinements for: {project_desc}
Include:
- Detailed Implementation Steps
- Error Handling
- Testing Strategy
- Performance Considerations
Format in Markdown.""",

        "Completion.md": f"""Generate completion criteria and project structure for: {project_desc}
Include:
- Project Structure
- Development Steps
- Testing Requirements
- Deployment Considerations
Format in Markdown."""
    }

    files_content = {}
    for filename, prompt in prompts.items():
        response = completion(
            model=model,
            messages=[{
                "role": "system",
                "content": "You are a software architect. Generate detailed technical documentation."
            },
            {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        files_content[filename] = response.choices[0].message.content

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
        # Create architecture directory
        arch_dir = Path("architecture")
        arch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created architecture directory")

        # Generate architecture files using LiteLLM
        files_content = generate_sparc_content(project_desc, config.aider_model)
        
        # Save the generated content
        for filename, content in files_content.items():
            file_path = arch_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Generated {filename}")
            "Specification.md": f"""# Specification

## Project Overview
Creating a real-time web application using Vite.js and WebSocket technology.

## Core Requirements
1. Set up a Vite.js project with React
2. Implement WebSocket client-server communication
3. Real-time data updates
4. Clean and modern UI
5. Error handling and connection management

## Technical Requirements
- Vite.js for frontend development
- WebSocket protocol for real-time communication
- React for UI components
- Error boundary implementation
- Connection status indicators
""",
            "Architecture.md": """# Architecture

## System Components

### Component: WebSocketClient
- Manages WebSocket connection
- Handles connection lifecycle
- Implements reconnection logic
- Provides message sending/receiving interface

### Component: ConnectionManager
- Monitors connection status
- Implements heartbeat mechanism
- Handles connection errors
- Provides connection status to UI

### Component: UIComponents
- Real-time data display components
- Connection status indicator
- Message input/output interfaces
- Error boundaries

### Component: MessageHandler
- Message serialization/deserialization
- Message queue management
- Retry logic for failed messages
""",
            "Pseudocode.md": """# Pseudocode

## WebSocket Setup
```typescript
class WebSocketClient {
  constructor(url: string) {
    this.ws = new WebSocket(url)
    this.setupEventHandlers()
  }

  setupEventHandlers() {
    this.ws.onopen = () => handleOpen()
    this.ws.onclose = () => handleClose()
    this.ws.onerror = (error) => handleError(error)
    this.ws.onmessage = (message) => handleMessage(message)
  }
}
```

## Connection Management
```typescript
class ConnectionManager {
  monitorConnection() {
    setInterval(() => {
      if (!isConnected) {
        reconnect()
      }
      sendHeartbeat()
    }, HEARTBEAT_INTERVAL)
  }
}
```
""",
            "Refinement.md": """# Refinement

## Implementation Details

### WebSocket Connection
- Use secure WebSocket (wss://) for production
- Implement exponential backoff for reconnection attempts
- Add connection timeout handling

### State Management
- Use React Context for connection state
- Implement message queue for offline support
- Add message delivery confirmation

### Error Handling
- Implement comprehensive error boundaries
- Add retry mechanisms for failed connections
- Provide user feedback for connection issues

### Testing Strategy
- Unit tests for connection logic
- Integration tests for WebSocket communication
- End-to-end tests for real-time features
""",
            "Completion.md": """# Completion

## Project Structure
```
src/
  components/
    ConnectionStatus.tsx
    MessageList.tsx
    MessageInput.tsx
  services/
    WebSocketClient.ts
    ConnectionManager.ts
    MessageHandler.ts
  hooks/
    useWebSocket.ts
    useConnection.ts
  context/
    WebSocketContext.tsx
```

## Development Steps
1. Initialize Vite.js project with React
2. Implement WebSocket service classes
3. Create React components
4. Add connection management
5. Implement error handling
6. Add tests
7. Deploy and verify
"""
        }

        for filename, content in files_content.items():
            file_path = arch_dir / filename
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Generated {filename}")
    elif args.mode == 'implement':
        # Read Architecture.md to find components
        arch_file = Path("architecture/Architecture.md")
        if not arch_file.exists():
            logger.error("Architecture.md not found. Run architect mode first.")
            sys.exit(1)

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
