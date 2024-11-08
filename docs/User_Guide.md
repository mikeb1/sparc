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
```

Supported project types:
Any project description, for example:
- "fastapi backend"
- "fastapi using websockets"
- "swarm agents using denojs"
- "react frontend with typescript"

CLI Options:
- `--guidance-file` - Custom guidance TOML file
- `--model` - LiteLLM model choices:
  - claude-3-opus-20240229
  - claude-3-sonnet-20240229 (default)
  - gpt-4
  - gpt-4-turbo
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
- `OPENAI_API_KEY` - OpenAI API key
- `AIDER_MODEL` - Default model choice

## Troubleshooting

Common issues:
1. Missing API key - Set your LiteLLM API key
2. File generation errors - Check permissions and paths
3. Model errors - Verify model availability and API key
