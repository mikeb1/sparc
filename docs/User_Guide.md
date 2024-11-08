# User Guide

## Installation

1. Prerequisites:
   - Python 3.x
   - pip
   - Git (optional)

2. Install dependencies:
   ```bash
   pip install litellm toml
   ```

## Basic Usage

### Architect Mode
Generate architecture documentation:
```bash
python3 cli/sparc_cli.py architect "project-type"

# Output directory will be created as:
# architecture_YYYYMMDD_HHMMSS_project-name/
#   - Specification.md
#   - Architecture.md 
#   - Pseudocode.md
#   - Refinement.md
#   - Completion.md
#   - guidance.toml

# Progress and file generation will be logged:
# 2024-03-21 10:15:23 - INFO - Architecting project: my-project
# 2024-03-21 10:15:24 - INFO - Generated Specification.md (12,345 chars)
# ...
```

Supported project types:
The CLI accepts any free-form project description, such as:
- Web applications (e.g., "fastapi backend", "react frontend")
- Real-time systems (e.g., "websocket chat server", "event streaming")
- Specialized systems (e.g., "swarm agents", "distributed cache")
- Cross-platform apps (e.g., "electron desktop app", "flutter mobile app")

CLI Options:
- `--guidance-file` - Path to custom guidance TOML file (default: guidance.toml)
- `--model` - LiteLLM model selection:
  - claude-3-opus-20240229 (most capable)
  - claude-3-sonnet-20240229 (default, balanced)
  - gpt-4 (alternative)
  - gpt-4-turbo (faster alternative)
- `--temperature` - Model temperature (default: 0.7)
- `--max-tokens` - Maximum tokens (default: 4096)
- `--litellm-api-key` - API key for LiteLLM

### Implement Mode
Generate implementation code:
```bash
python3 cli/sparc_cli.py implement
```

Options:
- `--max-attempts` - Maximum implementation attempts (default: 3)
- Same model options as architect mode

## Configuration

### guidance.toml Format
```toml
[specification]
content = """
Your project specifications here
"""
```

### Environment Variables
- `LITELLM_API_KEY` - API key for model access
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI models)
- `ANTHROPIC_API_KEY` - Anthropic API key (if using Claude models)

## Troubleshooting

Common issues:
1. Missing API key - Set your LiteLLM API key
2. File generation errors - Check permissions and paths
3. Model errors - Verify model availability and API key
