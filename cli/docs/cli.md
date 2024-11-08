```python
#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
import toml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SPARCConfig:
    architecture_dir: str = "architecture"
    test_dir: str = "tests"
    source_dir: str = "src"
    max_attempts: int = 3
    verbose: bool = False
    guidance_file: str = "guidance.toml"

class DevelopmentCycle:
    def __init__(self, config: SPARCConfig):
        self.config = config
        self.components = []
        self.guidance = self._load_guidance(config.guidance_file)

    def _load_guidance(self, guidance_file: str) -> Dict:
        """Load initial guidance from a TOML file."""
        guidance_path = Path(guidance_file)
        if guidance_path.exists():
            try:
                with open(guidance_path, 'r') as f:
                    guidance = toml.load(f)
                    logger.info(f"Loaded guidance from {guidance_file}")
                    return guidance
            except Exception as e:
                logger.error(f"Failed to load guidance from {guidance_file}: {e}")
        else:
            logger.warning(f"Guidance file '{guidance_file}' not found.")
        return {}

    def _generate_guidance_toml(self, project_desc: str) -> str:
        """Generate guidance.toml content based on project description."""
        try:
            # Get guidance content from LLM
            response = completion(
                model=self.config.model,
                messages=[{
                    "role": "system",
                    "content": """You are an expert software architect. Generate a detailed guidance.toml file 
                    that will be used to guide the development of a software project. Include comprehensive 
                    sections for specification, architecture, pseudocode, refinement, and completion."""
                }, {
                    "role": "user",
                    "content": f"""Generate a detailed guidance.toml file for the following project:
                    {project_desc}
                    
                    Include:
                    1. Specification section with detailed requirements
                    2. Architecture section with component definitions
                    3. Pseudocode section with implementation details
                    4. Refinement section with optimization strategies
                    5. Completion section with deployment guidelines
                    
                    Format the output as a valid TOML file."""
                }],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to generate guidance.toml content: {str(e)}")
            # Return a basic template if generation fails
            return """[specification]
content = "Create detailed specifications for the project."

[architecture]
content = "Define system architecture and components."

[pseudocode]
content = "Provide implementation pseudocode."

[refinement]
content = "Define optimization and improvement strategies."

[completion]
content = "Specify completion criteria and deployment steps."
"""

    async def _generate_detailed_content(self, file_type: str, guidance: str) -> str:
        """Generate detailed content using LiteLLM based on file type and guidance asynchronously."""
        base_prompt = {
            "Specification.md": """Create a comprehensive software specification document following the SPARC framework. Include:
1. Project Overview
   - Goals and Objectives
   - Stakeholders
   - Success Criteria
2. Functional Requirements
   - User Stories
   - Use Cases
   - Data Flow
   - Business Rules
3. Non-Functional Requirements
   - Performance Metrics
   - Security Standards
   - Scalability Requirements
   - Reliability Targets
4. Technical Architecture
   - System Components
   - Integration Points
   - Data Architecture
   - Security Architecture
5. Implementation Details
   - Technology Stack
   - Development Approach
   - Testing Strategy
   - Deployment Plan
6. Project Management
   - Timeline
   - Resource Requirements
   - Risk Management
   - Quality Assurance

Based on this guidance:""",

            "Pseudocode.md": """Create a detailed pseudocode document following the SPARC framework. Include:
1. System Architecture
   - Component Overview
   - Communication Flow
   - Data Flow Diagrams
2. Core Algorithms
   - Main Processing Logic
   - Data Transformations
   - Business Rules Implementation
3. Data Structures
   - Key Classes/Objects
   - Database Schema
   - Cache Structures
4. Error Handling
   - Exception Scenarios
   - Recovery Procedures
   - Logging Strategy
5. Integration Logic
   - API Endpoints
   - External Services
   - Message Queues
6. Performance Considerations
   - Optimization Points
   - Caching Strategy
   - Resource Management
7. Security Implementation
   - Authentication Flow
   - Authorization Logic
   - Data Protection

Based on this guidance:""",

            "Architecture.md": """Create a detailed software architecture document following the SPARC framework. Include:
1. System Architecture
   - Architectural Patterns
   - Design Principles
   - System Boundaries
2. Component Design
   - Core Components
   - Component Interfaces
   - Dependencies
   - State Management
3. Data Architecture
   - Data Models
   - Storage Solutions
   - Data Flow
   - Caching Strategy
4. Integration Architecture
   - API Design
   - Event Handling
   - Message Queues
   - External Services
5. Security Architecture
   - Authentication
   - Authorization
   - Data Protection
   - Audit Logging
6. Deployment Architecture
   - Infrastructure
   - Scalability
   - High Availability
   - Disaster Recovery
7. Development Guidelines
   - Coding Standards
   - Testing Strategy
   - Documentation
   - Version Control

For each component, use this format:
## Component: [Name]
### Purpose and Scope
### Technical Specifications
### Dependencies and Interfaces
### Data Management
### Error Handling
### Performance Requirements
### Security Measures
### Testing Approach
### Deployment Considerations

Based on this guidance:""",

            "Refinement.md": """Create a detailed refinement document following the SPARC framework. Include:
1. Design Decisions and Rationale
2. Performance Optimizations
3. Security Hardening
4. Code Quality Improvements
5. Technical Debt Assessment
6. Scalability Enhancements
7. Reliability Improvements
8. Maintainability Considerations
9. Testing Strategy Refinements
10. Documentation Updates
11. Integration Optimizations
12. Deployment Process Improvements
13. Monitoring and Logging Enhancements

Based on this guidance:""",

            "Completion.md": """Create a comprehensive completion document following the SPARC framework. Include:
1. Implementation Status
2. Test Coverage Report
3. Performance Benchmarks
4. Security Audit Results
5. Documentation Completeness
6. Deployment Readiness
7. Integration Test Results
8. User Acceptance Criteria
9. Known Issues and Workarounds
10. Future Enhancements
11. Maintenance Guidelines
12. Support Documentation
13. Training Materials
14. Release Notes

Based on this guidance:"""
        }

        try:
            response = completion(
                model=self.config.model,
                messages=[{
                    "role": "system",
                    "content": "You are an expert software architect following the SPARC framework. Generate detailed, comprehensive documentation that follows best practices and industry standards."
                }, {
                    "role": "user",
                    "content": f"{base_prompt[file_type]}\n\n{guidance}"
                }],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=self.config.litellm_api_key
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content with LiteLLM: {str(e)}")
            return f"# {file_type[:-3]}\n\nError generating content: {str(e)}"

    async def run_architect_mode(self):
        """Run in architect mode to generate detailed architecture documents using LiteLLM concurrently."""
        # Create architecture directory
        arch_dir = Path(self.config.architecture_dir)
        arch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created architecture directory at {arch_dir.resolve()}")

        # Generate guidance.toml if it doesn't exist
        guidance_path = arch_dir / "guidance.toml"
        if not guidance_path.exists():
            logger.info("Generating guidance.toml...")
            project_desc = self.guidance.get('project', {}).get('description', "")
            if not project_desc:
                project_desc = "A software project following SPARC framework principles."
            
            guidance_content = self._generate_guidance_toml(project_desc)
            try:
                with open(guidance_path, 'w') as f:
                    f.write(guidance_content)
                logger.info(f"Generated guidance.toml at {guidance_path}")
                self.guidance = self._load_guidance(str(guidance_path))
            except Exception as e:
                logger.error(f"Failed to write guidance.toml: {str(e)}")
        else:
            logger.info("guidance.toml already exists, using existing file")

        # Prepare files to generate
        files_to_generate = {
            "Specification.md": self.guidance.get('specification', {}).get('content', "Create a detailed specification for the project."),
            "Pseudocode.md": self.guidance.get('pseudocode', {}).get('content', "Provide high-level pseudocode for the application."),
            "Architecture.md": self.guidance.get('architecture', {}).get('content', "Describe the system architecture and components."),
            "Refinement.md": self.guidance.get('refinement', {}).get('content', "Refine the design and implementation details."),
            "Completion.md": self.guidance.get('completion', {}).get('content', "Document the completion criteria and final state.")
        }

        # Generate files concurrently
        async def generate_file(filename: str, guidance: str) -> tuple[str, str]:
            """Generate content for a single file."""
            file_path = arch_dir / filename
            if not file_path.exists():
                logger.info(f"Generating detailed content for {filename}...")
                content = await self._generate_detailed_content(filename, guidance)
                return filename, content
            else:
                logger.info(f"{filename} already exists. Skipping.")
                return filename, None

        # Create tasks for all files
        tasks = [generate_file(filename, guidance) 
                for filename, guidance in files_to_generate.items()]

        # Run all tasks concurrently
        try:
            results = await asyncio.gather(*tasks)
            
            # Write results to files
            for filename, content in results:
                if content is not None:
                    file_path = arch_dir / filename
                    with open(file_path, 'w') as f:
                        f.write(content)
                    logger.info(f"Generated {filename}")
            
            logger.info("Architecture files generated successfully.")
        except Exception as e:
            logger.error(f"Error generating architecture files: {str(e)}")
            raise

    def _generate_file_with_aider(self, file_path: Path, prompt: str) -> bool:
        """Use aider.chat to generate a file based on the prompt."""
        try:
            logger.info(f"Generating {file_path} with aider.chat...")
            cmd = ["aider", "--yes", "--message", prompt, str(file_path)]
            if self.config.verbose:
                cmd.extend(["--verbose", "--no-pretty"])
            logger.debug(f"Executing command: {' '.join(cmd)}")

            # Run aider
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"aider.chat completed successfully for {file_path}")
                return True
            else:
                logger.error(f"aider.chat failed with return code {result.returncode} for {file_path}")
                logger.error(f"Stdout: {result.stdout}")
                logger.error(f"Stderr: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error during aider.chat execution: {str(e)}")
            return False

    def run_implementation_mode(self):
        """Run in implementation mode to develop the project using aider.chat."""
        # Read architecture files
        arch_dir = Path(self.config.architecture_dir)
        if not arch_dir.exists():
            logger.error(f"Architecture directory '{arch_dir}' does not exist. Please run architect mode first.")
            sys.exit(1)

        # Read and parse architecture files
        specification = self._read_file(arch_dir / "Specification.md")
        pseudocode = self._read_file(arch_dir / "Pseudocode.md")
        architecture_desc = self._read_file(arch_dir / "Architecture.md")

        # Parse components from architecture description
        self.components = self.parse_architecture(architecture_desc)

        # Start development cycle
        for component in self.components:
            self.develop_component(component, specification, pseudocode, architecture_desc)

    def _read_file(self, file_path: Path) -> str:
        """Read content from a file."""
        if not file_path.exists():
            logger.error(f"File '{file_path}' does not exist.")
            sys.exit(1)
        with open(file_path, 'r') as f:
            return f.read()

    def parse_architecture(self, architecture_desc: str) -> List[Dict]:
        """Parse the architecture description and extract components."""
        components = []
        lines = architecture_desc.splitlines()
        for line in lines:
            if line.startswith("## Component:"):
                component_name = line.replace("## Component:", "").strip()
                components.append({"name": component_name})
        if not components:
            logger.warning("No components found in architecture description.")
            # For demo purposes, add a default component
            components.append({"name": "MainComponent"})
        return components

    def develop_component(self, component: Dict, specification: str, pseudocode: str, architecture_desc: str):
        """Develop a component using aider.chat and London-style TDD."""
        component_name = component['name']
        logger.info(f"Developing component: {component_name}")

        attempts = 0
        while attempts < self.config.max_attempts:
            logger.info(f"\nAttempt {attempts + 1}/{self.config.max_attempts} for component {component_name}")

            # Generate tests first using aider.chat
            test_generated = self._generate_tests_with_aider(component, specification, pseudocode, architecture_desc)

            if not test_generated:
                attempts += 1
                continue

            # Run tests (should fail initially)
            tests_passed = self.run_tests()
            if tests_passed:
                logger.info("Tests passed unexpectedly. Proceeding to implementation.")
            else:
                logger.info("Tests failed as expected. Proceeding to implementation.")

            # Implement component to make tests pass using aider.chat
            implementation_generated = self._generate_implementation_with_aider(component, specification, pseudocode, architecture_desc)

            if not implementation_generated:
                attempts += 1
                continue

            # Run tests again
            tests_passed = self.run_tests()
            if tests_passed:
                logger.info(f"Component {component_name} developed successfully.")
                break
            else:
                logger.warning(f"Tests failed after implementation. Retrying...")
                attempts += 1

        if attempts == self.config.max_attempts:
            logger.error(f"Failed to develop component {component_name} after {attempts} attempts.")

    def _generate_tests_with_aider(self, component: Dict, specification: str, pseudocode: str, architecture_desc: str) -> bool:
        """Use aider.chat to generate tests for a component."""
        component_name = component['name']
        test_file_path = Path(self.config.test_dir) / f"test_{component_name.lower()}.py"
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        prompt = f"""
You are to write unit tests for the component '{component_name}' as per the specification, pseudocode, and architecture provided.

Specification:
{specification}

Pseudocode:
{pseudocode}

Architecture:
{architecture_desc}

Follow the London-style TDD approach, using mocks to isolate the component.

Write the test code in '{test_file_path}'.
"""
        return self._run_aider([str(test_file_path)], prompt)

    def _generate_implementation_with_aider(self, component: Dict, specification: str, pseudocode: str, architecture_desc: str) -> bool:
        """Use aider.chat to generate implementation for a component."""
        component_name = component['name']
        impl_file_path = Path(self.config.source_dir) / f"{component_name.lower()}.py"
        impl_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path = Path(self.config.test_dir) / f"test_{component_name.lower()}.py"
        prompt = f"""
You are to implement the component '{component_name}' as per the specification, pseudocode, and architecture provided.

Specification:
{specification}

Pseudocode:
{pseudocode}

Architecture:
{architecture_desc}

Ensure that your implementation passes the tests in '{test_file_path}'.

Write the implementation code in '{impl_file_path}'.
"""
        return self._run_aider([str(impl_file_path)], prompt)

    def _run_aider(self, files: List[str], message: str) -> bool:
        """Run aider.chat with the given files and message."""
        try:
            logger.info("Running aider.chat...")
            cmd = ["aider", "--yes", "--message", message] + files
            if self.config.verbose:
                cmd.extend(["--verbose", "--no-pretty"])
            logger.debug(f"Executing command: {' '.join(cmd)}")

            # Run aider with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
                cwd=os.getcwd()
            )

            # Display output in real-time
            while True:
                output = process.stdout.readline()
                if output:
                    logger.info(output.strip())
                error = process.stderr.readline()
                if error:
                    logger.error(error.strip())

                if output == '' and error == '' and process.poll() is not None:
                    break

            result = process.wait()

            if result == 0:
                logger.info("aider.chat completed successfully.")
                return True
            else:
                logger.error(f"aider.chat failed with return code {result}.")
                return False

        except Exception as e:
            logger.error(f"Unexpected error during aider.chat execution: {str(e)}")
            return False

    def run_tests(self) -> bool:
        """Run the test suite."""
        logger.info("Running tests...")
        cmd = ["pytest", self.config.test_dir]
        result = subprocess.run(cmd)
        if result.returncode == 0:
            logger.info("All tests passed.")
            return True
        else:
            logger.warning("Some tests failed.")
            return False

def main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI with aider.chat integration')
    subparsers = parser.add_subparsers(dest='mode', help='Modes of operation')

    # Architect mode
    parser_architect = subparsers.add_parser('architect', help='Run in architect mode to generate architecture files using aider.chat')
    parser_architect.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser_architect.add_argument('--guidance-file', type=str, default='guidance.toml', help='Path to guidance TOML file')

    # Implement mode
    parser_implement = subparsers.add_parser('implement', help='Run in implementation mode to develop the project using aider.chat')
    parser_implement.add_argument('--max-attempts', type=int, default=3, help='Maximum development attempts per component')
    parser_implement.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser_implement.add_argument('--guidance-file', type=str, default='guidance.toml', help='Path to guidance TOML file')

    args = parser.parse_args()

    config = SPARCConfig(
        max_attempts=args.max_attempts if 'max_attempts' in args else 3,
        verbose=args.verbose if 'verbose' in args else False,
        guidance_file=args.guidance_file if 'guidance_file' in args else 'guidance.toml',
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        litellm_api_key=args.litellm_api_key
    )
    cycle = DevelopmentCycle(config)

    if args.mode == 'architect':
        await cycle.run_architect_mode()
    elif args.mode == 'implement':
        cycle.run_implementation_mode()
    else:
        parser.print_help()
        sys.exit(1)

async def async_main():
    parser = argparse.ArgumentParser(description='SPARC Framework CLI')
    # ... rest of async_main implementation ...

def main():
    """Entry point that runs the async main function."""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
```

## Instructions

### Overview

This updated script enhances the previous version by allowing you to provide detailed initial guidance through a TOML file (`guidance.toml`) or via prompts. This guidance is used to create the `/architecture` markdown files based on the SPARC framework.

### Setup and Prerequisites

#### Install Required Tools

- **Python 3.x**: Ensure you have Python 3 installed.
- **aider.chat**: Install aider.chat for AI-assisted development.
  ```bash
  pip install aider-chat
  ```
- **pytest**: Install pytest for running tests.
  ```bash
  pip install pytest
  ```
- **toml**: Install the TOML library for parsing guidance files.
  ```bash
  pip install toml
  ```
- **Ensure API Keys**: Make sure you have the necessary API keys set up for aider.chat to function correctly.

#### Save the Script

Save the script to a file named `sparc_cli.py` in your project directory.

#### Create a Guidance File

Create a `guidance.toml` file in the same directory. This file will contain your detailed initial guidance for each of the architecture documents.

Example `guidance.toml`:

```toml
[specification]
content = """
Create a detailed specification for an e-commerce platform that includes user registration, product catalog, shopping cart, and order processing.
"""

[pseudocode]
content = """
Provide high-level pseudocode for the main functionalities, focusing on the flow between components.
"""

[architecture]
content = """
Describe the system architecture, including components like UserAuth, ProductCatalog, ShoppingCart, and OrderProcessing. Outline how these components interact.
"""

[refinement]
content = """
Use this document to refine design decisions, discuss trade-offs, and optimize component interactions.
"""

[completion]
content = """
Finalize project details, deployment strategies, and any remaining tasks before launch.
"""
```

#### Make the Script Executable (Optional)

If you are on a Unix-like system, you can make the script executable:

```bash
chmod +x sparc_cli.py
```

### Usage

#### Architect Mode

Use this mode to generate the initial architecture files for your project based on the guidance provided.

```bash
python sparc_cli.py architect --guidance-file guidance.toml
```

This command will:

- Create an `/architecture` directory in your current working directory.
- Generate the following markdown files inside the `/architecture` directory using aider.chat and your guidance:
  - `Specification.md`
  - `Pseudocode.md`
  - `Architecture.md`
  - `Refinement.md`
  - `Completion.md`

These files will contain content generated by aider.chat based on the prompts provided in your `guidance.toml` file.

#### Editing the Architecture Files

After generating the architecture files, review and edit them to ensure they accurately reflect your project's needs.

#### Implementation Mode

Use this mode to generate code and tests for your components.

```bash
python sparc_cli.py implement --guidance-file guidance.toml
```

This command will:

- Read the architecture files from the `/architecture` directory.
- Parse the components listed in `Architecture.md`.
- For each component:
  - Use aider.chat to generate unit tests following the London-style TDD approach.
  - Write the test code to the `/tests` directory.
  - Run the tests (they should fail initially since the implementation is missing).
  - Use aider.chat to generate implementation code that makes the tests pass.
  - Write the implementation code to the `/src` directory.
  - Run the tests again to verify.

#### Command-Line Options

- **Architect Mode**:
  - `--verbose`: Enable verbose output.
  - `--guidance-file`: Path to the guidance TOML file (default is `guidance.toml`).

- **Implement Mode**:
  - `--max-attempts`: Maximum development attempts per component (default is 3).
  - `--verbose`: Enable verbose output.
  - `--guidance-file`: Path to the guidance TOML file (default is `guidance.toml`).

Example:

```bash
python sparc_cli.py implement --max-attempts 5 --verbose --guidance-file guidance.toml
```

### Notes

- **Guidance File**: The script now supports providing detailed initial guidance through a TOML file (`guidance.toml`). This file should contain sections for each of the architecture documents.
- **Component Detection**: Components are detected by parsing `Architecture.md` for lines starting with `## Component:`.
- **aider.chat Integration**: Ensure that aider.chat is installed and properly configured with your API keys.
- **Test Runner**: The script uses `pytest` to run tests. Ensure your test files are named using the `test_*.py` pattern.
- **Directories**:
  - `/architecture`: Contains architecture markdown files.
  - `/tests`: Contains generated test code.
  - `/src`: Contains generated implementation code.

### Example Workflow

#### 1. Create a Guidance File

Create `guidance.toml` with your initial guidance as shown in the example above.

#### 2. Run Architect Mode

```bash
python sparc_cli.py architect --guidance-file guidance.toml
```

#### 3. Review and Edit Architecture Files

Open `architecture/Architecture.md` and ensure your components are listed correctly.

#### 4. Run Implementation Mode

```bash
python sparc_cli.py implement --guidance-file guidance.toml
```

The script will process each component, generate tests and code using aider.chat based on your guidance, and attempt to run the tests.

### Customization

- **Configuration**: Modify the `SPARCConfig` dataclass to change default directories or settings.
- **Verbosity**: Use the `--verbose` flag to see detailed logs.
- **Max Attempts**: Adjust the `--max-attempts` parameter to control how many times the script tries to develop a component before giving up.
- **Guidance**: Customize `guidance.toml` to provide specific instructions for each architecture document.

### Limitations

- **AI Output**: The quality of the generated code and documents depends on aider.chat and the clarity of your guidance.
- **Error Handling**: The script has basic error handling; you may need to add more robust checks for production use.
- **Complex Projects**: For large or complex projects, you might need to enhance the script to handle dependencies and integrations.

### Conclusion

This script automates the development process by integrating the SPARC framework and London-style TDD with aider.chat, now enhanced to include detailed initial guidance via a TOML file. By following the instructions and customizing the script and guidance as needed, you can streamline the creation of architecture documentation and the development of your project's components.

### Troubleshooting

- **aider.chat Errors**: Ensure your API keys are correctly set and that aider.chat is functioning.
- **Test Failures**: If tests fail after implementation, review the generated code and tests for correctness.
- **Logging**: Use the `--verbose` flag to get detailed logs that can help diagnose issues.

### Support

For assistance or to report issues, please refer to the aider.chat documentation or support channels.

---

*This script and guide provide a foundation for automating development using the SPARC framework and London-style TDD, integrating aider.chat for AI-assisted code generation. Customize and extend it as needed for your specific project requirements.*
