# API Documentation

## CLI Commands

### architect
```bash
python3 cli/sparc_cli.py architect "project description" [options]
```

Options:
- `project description`: Free-form description of the project to architect
- `--guidance-file`: Path to guidance TOML file (default: guidance.toml)
- `--model`: LiteLLM model choices (default: claude-3-sonnet-20240229):
  - claude-3-opus-20240229 (most capable, largest context)
  - claude-3-sonnet-20240229 (balanced performance/cost)
  - gpt-4 (alternative option)
  - gpt-4-turbo (faster alternative)

The architect mode:
1. Analyzes the project description
2. Creates a timestamped architecture directory
3. Generates comprehensive documentation:
   - Specification.md - Detailed requirements
   - Architecture.md - System design
   - Pseudocode.md - Implementation guidance
   - Refinement.md - Implementation details
   - Completion.md - Completion criteria
   - guidance.toml - Configuration
4. Provides progress logging for each generated file

### implement
```bash
python3 cli/sparc_cli.py implement [options]
```

Options:
- `--max-attempts`: Maximum implementation attempts (default: 3)
- `--guidance-file`: Path to guidance file
- Model options (same as architect)

The implement mode uses a test-driven development (TDD) approach:
1. Creates a timestamped implementation directory with src/ and tests/
2. For each component:
   - Generates comprehensive test files first
   - Uses aider to implement the component to pass tests
   - Provides real-time progress and error logging
   - Runs tests with visual feedback
   - Reports test results and implementation status

Implementation uses the aider tool with:
- Auto-confirmation of prompts
- Diff-based edit format
- 5-minute timeout per component
- Comprehensive error handling

### Generated Code Structure
- `src/` directory:
  - Agent management (`agent/`)
  - Monitoring services (`monitoring/`)
  - State management (`state/`)
  - Communication services (`communication/`)
  
- `tests/` directory:
  - Unit tests for each component
  - Integration tests
  - Test fixtures and utilities

## Configuration

### SPARCConfig
```python
@dataclass
class SPARCConfig:
    architecture_dir: str = "architecture"
    test_dir: str = "tests"
    source_dir: str = "src"
    max_attempts: int = 3
    verbose: bool = False
    guidance_file: str = "guidance.toml"
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4096
    litellm_api_key: Optional[str] = None
    use_git: bool = True
    auto_commits: bool = True
    dirty_commits: bool = True
    auto_test: bool = False
    test_cmd: Optional[str] = None
```
