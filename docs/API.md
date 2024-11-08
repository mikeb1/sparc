# API Documentation

## CLI Commands

### architect
```bash
python3 cli/sparc_cli.py architect [project_type] [options]
```

Options:
- `project_type`: Type of project to architect
- `--guidance-file`: Path to guidance TOML file
- `--model`: LiteLLM model name
- `--temperature`: Model temperature
- `--max-tokens`: Maximum tokens
- `--litellm-api-key`: API key

### implement
```bash
python3 cli/sparc_cli.py implement [options]
```

Options:
- `--max-attempts`: Maximum implementation attempts
- Model options (same as architect)

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
# API Documentation

## CLI Commands

### architect
```bash
python3 cli/sparc_cli.py architect [project_type] [options]
```

Options:
- `project_type`: Type of project to architect
- `--guidance-file`: Path to guidance TOML file
- `--model`: LiteLLM model name
- `--temperature`: Model temperature
- `--max-tokens`: Maximum tokens
- `--litellm-api-key`: API key

### implement
```bash
python3 cli/sparc_cli.py implement [options]
```

Options:
- `--max-attempts`: Maximum implementation attempts
- Model options (same as architect)

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
