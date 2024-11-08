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
Format in Markdown.
# Refinement.md

## Detailed Implementation Steps

1. **Set Up the Development Environment**
    - **Install Dependencies**:
        - [List necessary dependencies here]
    - **Create Virtual Environment or Equivalent**:
        - [Instructions for setting up the environment]

2. **Implement Core Services**
    - **ServiceName**
        - [Implementation steps]
    - **AnotherServiceName**
        - [Implementation steps]

3. **Define Models**
    - Create models/entities with necessary fields and relationships.

4. **Implement API Endpoints or Equivalent**
    - Set up the application framework.
    - Define routes/endpoints for various functionalities.
    - Integrate services within endpoint handlers using dependency injection or equivalent.

5. **Configure Dependency Injection or Equivalent**
    - Set up dependency injection to manage service dependencies.

6. **Set Up Configuration Management**
    - Define configuration settings (e.g., secret keys, database URLs) using environment variables or configuration files.

7. **Implement Security Measures**
    - Secure API endpoints using authentication and authorization mechanisms.
    - Implement role-based access control.

8. **Initialize Database**
    - Set up the database and run migrations or create tables as necessary.

## Error Handling

1. **Validation Errors**
    - Validate incoming request data.
    - Return appropriate error responses when validation fails.

2. **Authentication Errors**
    - Handle invalid credentials by returning appropriate error responses.
    - Use standardized error responses.

3. **Authorization Errors**
    - Enforce role-based access control.
    - Return appropriate error responses when access is denied.

4. **Database Errors**
    - Catch database exceptions and return appropriate error responses.
    - Log detailed error information for debugging purposes.

5. **Not Found Errors**
    - Return appropriate error responses when requested resources do not exist.

6. **Global Exception Handling**
    - Implement a global exception handler to catch unhandled exceptions.
    - Ensure consistent error response format across the application.

## Testing Strategy

### Test-Driven Development (TDD) with the London Method

The testing strategy follows the London method of TDD, emphasizing behavior verification through interaction testing using mocks. This approach ensures that each unit of code is tested in isolation, focusing on its interactions with collaborators.

#### Steps to Implement London Method TDD

1. **Identify the Unit Under Test**
    - Determine the specific class or method to implement.

2. **Define the Expected Behavior**
    - Clearly outline what the unit is supposed to do and how it interacts with other components.

3. **Write a Failing Test for the Expected Behavior**
    - Use a testing framework to create tests.
    - Mock collaborators to isolate the unit.
    - Example Test:
        ```pseudo
        def test_method():
            mock_dependency = Mock()
            # Define expectations
            # Invoke method under test
            # Assert expectations
        ```

4. **Set Up Mocks and Expectations**
    - Mock external dependencies.
    - Define expectations on method calls, parameters, and return values.

5. **Run the Test and See It Fail**
    - Execute the test suite to ensure the new test fails, indicating the behavior is not yet implemented.

6. **Write the Minimum Code to Make the Test Pass**
    - Implement the necessary functionality in the unit to satisfy the test.

7. **Run the Test and See It Pass**
    - Re-run the test suite to verify the new test passes.
    - Ensure all existing tests remain passing.

8. **Refactor the Code**
    - Improve code quality without altering functionality.
    - Clean up code structure, remove redundancies, and enhance readability.
    - Re-run tests to ensure they still pass post-refactoring.

9. **Repeat the Cycle**
    - Move on to the next piece of functionality.
    - Continue writing tests, implementing code, and refactoring iteratively.

#### Advantages of Using the London Method

- **Isolation**: Ensures units are tested independently from their dependencies.
- **Behavior Focused**: Emphasizes the expected interactions, leading to better design.
- **Fast Feedback**: Quickly identifies issues in unit behavior.

#### Best Practices

- **Use Descriptive Test Names**: Clearly indicate what behavior is being tested.
    - Example: `test_processOrder_sendsConfirmationEmail`
- **Mock Only External Collaborators**: Avoid mocking internal components or simple data structures.
- **Verify Interactions Precisely**: Set strict expectations on mock interactions to ensure correct behavior.
- **Keep Tests Independent**: Ensure tests do not rely on the outcome of other tests.
- **Limit Over-Mocking**: Use real objects when mocking does not provide significant benefits.

## Performance Considerations

1. **Optimize Database Queries**
    - Use efficient query patterns.
    - Implement indexing on frequently queried fields.

2. **Implement Caching**
    - Cache results of expensive operations or frequent queries to reduce load times.

3. **Asynchronous Processing**
    - Utilize asynchronous programming to handle multiple requests concurrently.

4. **Resource Management**
    - Ensure proper management of database connections and other resources to prevent leaks.

5. **Load Testing**
    - Conduct load tests to identify performance bottlenecks.
    - Use appropriate tools for simulating high traffic.

6. **Monitoring and Logging**
    - Implement monitoring to track performance metrics.
    - Use logging to identify and troubleshoot performance issues.

7. **Scalability Planning**
    - Design the system to scale horizontally or vertically as needed.
    - Consider using containerization and orchestration tools for scaling.

8. **Code Optimization**
    - Profile the application to identify slow code paths.
    - Optimize algorithms and data structures for better performance.

9. **Security Implications of Performance Enhancements**
    - Ensure that performance optimizations do not compromise security.
    - For example, caching sensitive data should be handled securely.
""",

        "Completion.md": f"""Generate completion criteria and project structure for: {project_desc}
Include:
- Project Structure
- Development Steps
- Testing Requirements
- Deployment Considerations
# Completion.md

## Objective
Finalize the project, ensuring it is ready for deployment and meets all specified requirements, with a focus on integration and scalability.

## Tasks
- **Extensive Testing**:
  - Conduct unit tests for all core functionalities and dependencies.
  - Test authentication and authorization flows.
  - Verify data operations and database interactions.
  - Execute integration tests for all application interfaces and endpoints.
  - Validate data models and schema validations.
  - Test security features and access controls.
  - Ensure third-party integrations function correctly.
  - Achieve comprehensive test coverage using appropriate testing tools.

- **Compliance and Quality Assurance**:
  - Ensure the application meets all scalability, usability, and robustness criteria.
  - Conduct security audits to identify and mitigate vulnerabilities.
  - Perform performance testing to ensure the application meets speed and efficiency requirements.
  - Verify API key management and security best practices.
  - Monitor and optimize resource usage and operational costs.

- **Deployment and Rollback Plans**:
  - Prepare detailed deployment plans, including steps for deploying the application to production environments.
  - Develop rollback plans to revert changes in case of deployment issues.
  - Automate deployment processes using CI/CD pipelines where possible.
  - Ensure environment configurations are consistent across development, staging, and production.

- **Documentation and Support Materials**:
  - Create comprehensive user documentation, including user guides and FAQs.
  - Develop technical documentation for developers and maintainers.
  - Prepare training materials and support resources for end-users.
  - Document configuration options and best practices.
  - Include examples of different configurations and their use cases.

- **Post-Deployment Monitoring and Maintenance**:
  - Set up monitoring tools to track application performance and user activity.
  - Plan for regular maintenance and updates to address bugs and introduce new features.
  - Establish a feedback loop with users to gather insights and improve the application.
  - Monitor system health and respond to incidents promptly.

- **Final Review and Sign-Off**:
  - Conduct a final review with stakeholders to ensure all requirements are met.
  - Obtain formal sign-off from stakeholders, confirming project completion.
  - Ensure all deliverables are handed over appropriately and all documentation is up to date.

## Reflection
- **Overall Development Process**:
  - Reflect on the entire development process, identifying strengths and areas for improvement.
  - Discuss how effectively the development framework guided the project from start to finish.

- **Lessons Learned**:
  - Identify key lessons learned during the project, including challenges faced and solutions implemented.
  - Document best practices and strategies for future projects.

- **Project Goals and Requirements**:
  - Confirm that all project goals and requirements have been met satisfactorily.
  - Evaluate the project's success in achieving its intended outcomes.

- **Future Updates and Enhancements**:
  - Plan for future updates and enhancements based on user feedback and emerging needs.
  - Consider potential areas for innovation and improvement in subsequent versions.

- **Effectiveness of Development Framework**:
  - Discuss the effectiveness of the development framework in guiding the project.
  - Provide feedback on the framework's strengths and potential areas for refinement.

---

Format in Markdown.

"""
    }

    files_content = {}
    for filename, prompt in prompts.items():
        logger.info(f"Generating {filename}...")
        try:
            logger.info(f"Requesting {filename} from {model}...")
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
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Saved {filename} to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save {filename}: {str(e)}")
                raise
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
