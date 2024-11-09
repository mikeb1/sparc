Here's a comprehensive elaboration of Aider's advanced features and options:

## Advanced Configuration Options

### Model Selection
```python
# GPT-4 and GPT-3.5 Options
aider --4o                 # GPT-4o (default)
aider --4-turbo           # GPT-4 Turbo
aider --35turbo           # GPT-3.5 Turbo
aider --mini             # GPT-4o-mini
aider --model o1-preview # OpenAI preview models

# Claude Integration
export ANTHROPIC_API_KEY=<key>
aider --model claude-3-opus-20240229
aider --model claude-3-sonnet-20240229
```

### Edit Formats
```python
# Available edit formats
aider --edit-format whole   # Whole file editing (GPT-3.5 default)
aider --edit-format diff    # Edit block format (GPT-4 default)
aider --edit-format udiff   # Universal diff format (GPT-4 Turbo default)
aider --architect          # Architect mode for complex edits
```

## Advanced Features

### Repository Management
```python
# Git Integration
aider --commit "Custom commit message"  # Force commit with message
aider --auto-commits                    # Enable automatic commits
aider --dirty-commits                   # Allow commits on dirty repo
aider --attribute-commit-message        # Prefix commits with 'aider:'

# File Operations
aider --files "src/*.py" "tests/*.py"  # Multiple file patterns
aider --read-only "docs/*.md"          # Add read-only files
```

### Performance Optimization
```python
# Token Management
aider --max-tokens 4000                # Set max tokens per request
aider --max-chat-history-tokens 8000   # Set chat history limit
aider --stream                         # Enable streaming responses
```

## Development Tools

### Debugging Options
```python
# Debug Modes
aider --verbose --no-pretty  # Show raw LLM communication
aider --dry-run             # Test without making changes
aider --show-diffs          # Display diffs before applying

# Custom Prompts
aider --system-prompt "path/to/prompt.txt"  # Custom system prompt
aider --edit-format custom                  # Custom edit format
```

### API Configuration
```python
# API Settings
aider --openai-api-base "custom_endpoint"
aider --verify-ssl                      # SSL verification
aider --timeout 60                      # API timeout in seconds
aider --rate-limit 20                   # Requests per minute
```

## Scripting Integration

### Command Line Automation
```python
# Single Command Mode
aider --message "add type hints"        # One-shot execution
aider --message-file "instructions.txt" # Execute from file

# Batch Processing
aider --yes --auto-commits             # Non-interactive mode
aider --output-file "changes.log"      # Log changes
```

### Python API Usage
```python
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput

# Custom Configuration
io = InputOutput(yes=True, pretty=False)
model = Model("gpt-4-turbo", temperature=0.7)

# Initialize with Options
coder = Coder.create(
    main_model=model,
    fnames=["src/*.py"],
    io=io,
    auto_commits=True,
    dirty_commits=True,
    edit_format="udiff",
    max_tokens=8000
)
```

## Environment Configuration

### Environment Variables
```bash
# Core Settings
export AIDER_MODEL="gpt-4-turbo"
export AIDER_EDIT_FORMAT="udiff"
export AIDER_AUTO_COMMITS=true

# API Configuration
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export AIDER_API_BASE="custom-endpoint"
```

### Configuration File
```yaml
# .aider.config.yml
model: gpt-4-turbo
edit_format: udiff
auto_commits: true
max_tokens: 4000
system_prompt: custom_prompts/main.txt
commit_message_prefix: "feat:"
```

These advanced features and options provide extensive customization and control over Aider's behavior, allowing for efficient integration into various development workflows[1][2][3].
 
 # Configuration Options Reference

## Introduction

This document provides a comprehensive reference for all available configuration options in the `aider` command-line interface (CLI). You can use `aider --help` to see all available options or refer to the sections below for detailed information.

## Usage Summary

```bash
usage: aider [-h] [--openai-api-key] [--anthropic-api-key] [--model]
             [--opus] [--sonnet] [--haiku] [--4] [--4o] [--mini]
             [--4-turbo] [--35turbo] [--deepseek] [--o1-mini]
             [--o1-preview] [--list-models] [--openai-api-base]
             [--openai-api-type] [--openai-api-version]
             [--openai-api-deployment-id] [--openai-organization-id]
             [--model-settings-file] [--model-metadata-file]
             [--verify-ssl | --no-verify-ssl] [--edit-format]
             [--architect] [--weak-model] [--editor-model]
             [--editor-edit-format]
             [--show-model-warnings | --no-show-model-warnings]
             [--max-chat-history-tokens] [--env-file]
             [--cache-prompts | --no-cache-prompts]
             [--cache-keepalive-pings] [--map-tokens]
             [--map-refresh] [--map-multiplier-no-files]
             [--input-history-file] [--chat-history-file]
             [--restore-chat-history | --no-restore-chat-history]
             [--llm-history-file] [--dark-mode] [--light-mode]
             [--pretty | --no-pretty] [--stream | --no-stream]
             [--user-input-color] [--tool-output-color]
             [--tool-error-color] [--tool-warning-color]
             [--assistant-output-color] [--completion-menu-color]
             [--completion-menu-bg-color]
             [--completion-menu-current-color]
             [--completion-menu-current-bg-color] [--code-theme]
             [--show-diffs] [--git | --no-git]
             [--gitignore | --no-gitignore] [--aiderignore]
             [--subtree-only] [--auto-commits | --no-auto-commits]
             [--dirty-commits | --no-dirty-commits]
             [--attribute-author | --no-attribute-author]
             [--attribute-committer | --no-attribute-committer]
             [--attribute-commit-message-author | --no-attribute-commit-message-author]
             [--attribute-commit-message-committer | --no-attribute-commit-message-committer]
             [--commit] [--commit-prompt] [--dry-run | --no-dry-run]
             [--skip-sanity-check-repo] [--lint] [--lint-cmd]
             [--auto-lint | --no-auto-lint] [--test-cmd]
             [--auto-test | --no-auto-test] [--test]
             [--analytics | --no-analytics] [--analytics-log]
             [--analytics-disable] [--file] [--read] [--vim]
             [--chat-language] [--version] [--just-check-update]
             [--check-update | --no-check-update]
             [--install-main-branch] [--upgrade] [--apply]
             [--apply-clipboard-edits] [--yes-always] [-v]
             [--show-repo-map] [--show-prompts] [--exit] [--message]
             [--message-file] [--load] [--encoding] [-c]
             [--gui | --no-gui | --browser | --no-browser]
             [--suggest-shell-commands | --no-suggest-shell-commands]
             [--fancy-input | --no-fancy-input] [--voice-format]
             [--voice-language]
```

## Options Reference

### Main

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--help` | Show this help message and exit | | `-h` |
| `--openai-api-key OPENAI_API_KEY` | Specify the OpenAI API key | `OPENAI_API_KEY` | |
| `--anthropic-api-key ANTHROPIC_API_KEY` | Specify the Anthropic API key | `ANTHROPIC_API_KEY` | |
| `--model MODEL` | Specify the model to use for the main chat | `AIDER_MODEL` | |
| `--opus` | Use `claude-3-opus-20240229` model for the main chat | `AIDER_OPUS` | |
| `--sonnet` | Use `claude-3-5-sonnet-20241022` model for the main chat | `AIDER_SONNET` | |
| `--haiku` | Use `claude-3-5-haiku-20241022` model for the main chat | `AIDER_HAIKU` | |
| `--4` | Use `gpt-4-0613` model for the main chat | `AIDER_4` | `-4` |
| `--4o` | Use `gpt-4o-2024-08-06` model for the main chat | `AIDER_4O` | |
| `--mini` | Use `gpt-4o-mini` model for the main chat | `AIDER_MINI` | |
| `--4-turbo` | Use `gpt-4-1106-preview` model for the main chat | `AIDER_4_TURBO` | |
| `--35turbo` | Use `gpt-3.5-turbo` model for the main chat | `AIDER_35TURBO` | `--35-turbo`, `--3`, `-3` |
| `--deepseek` | Use `deepseek/deepseek-coder` model for the main chat | `AIDER_DEEPSEEK` | |
| `--o1-mini` | Use `o1-mini` model for the main chat | `AIDER_O1_MINI` | |
| `--o1-preview` | Use `o1-preview` model for the main chat | `AIDER_O1_PREVIEW` | |

### Model Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--list-models MODEL` | List known models which match the (partial) MODEL name | `AIDER_LIST_MODELS` | `--models` |
| `--openai-api-base OPENAI_API_BASE` | Specify the API base URL | `OPENAI_API_BASE` | |
| `--openai-api-type OPENAI_API_TYPE` | Specify the API type | `AIDER_API_TYPE` | |
| `--openai-api-version OPENAI_API_VERSION` | Specify the API version | `AIDER_API_VERSION` | |
| `--openai-api-deployment-id OPENAI_API_DEPLOYMENT_ID` | Specify the deployment ID | `AIDER_API_DEPLOYMENT_ID` | |
| `--openai-organization-id OPENAI_ORGANIZATION_ID` | Specify the OpenAI organization ID | `AIDER_ORGANIZATION_ID` | |
| `--model-settings-file MODEL_SETTINGS_FILE` | Specify a file with aider model settings for unknown models (default: `.aider.model.settings.yml`) | `AIDER_MODEL_SETTINGS_FILE` | |
| `--model-metadata-file MODEL_METADATA_FILE` | Specify a file with context window and costs for unknown models (default: `.aider.model.metadata.json`) | `AIDER_MODEL_METADATA_FILE` | |
| `--verify-ssl` | Verify the SSL cert when connecting to models (default: True) | `AIDER_VERIFY_SSL` | `--no-verify-ssl` |
| `--edit-format EDIT_FORMAT` | Specify what edit format the LLM should use (default depends on model) | `AIDER_EDIT_FORMAT` | `--chat-mode EDIT_FORMAT` |
| `--architect` | Use architect edit format for the main chat | `AIDER_ARCHITECT` | |
| `--weak-model WEAK_MODEL` | Specify the model to use for commit messages and chat history summarization (default depends on `--model`) | `AIDER_WEAK_MODEL` | |
| `--editor-model EDITOR_MODEL` | Specify the model to use for editor tasks (default depends on `--model`) | `AIDER_EDITOR_MODEL` | |
| `--editor-edit-format EDITOR_EDIT_FORMAT` | Specify the edit format for the editor model (default: depends on editor model) | `AIDER_EDITOR_EDIT_FORMAT` | |
| `--show-model-warnings` | Only work with models that have meta-data available (default: True) | `AIDER_SHOW_MODEL_WARNINGS` | `--no-show-model-warnings` |
| `--max-chat-history-tokens VALUE` | Soft limit on tokens for chat history, after which summarization begins. If unspecified, defaults to the model’s `max_chat_history_tokens` | `AIDER_MAX_CHAT_HISTORY_TOKENS` | |

### Cache Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--cache-prompts` | Enable caching of prompts (default: False) | `AIDER_CACHE_PROMPTS` | `--no-cache-prompts` |
| `--cache-keepalive-pings VALUE` | Number of times to ping at 5-minute intervals to keep prompt cache warm (default: 0) | `AIDER_CACHE_KEEPALIVE_PINGS` | |

### Repomap Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--map-tokens VALUE` | Suggested number of tokens to use for repo map; use `0` to disable (default: 1024) | `AIDER_MAP_TOKENS` | |
| `--map-refresh VALUE` | Control how often the repo map is refreshed. Options: `auto`, `always`, `files`, `manual` (default: `auto`) | `AIDER_MAP_REFRESH` | |
| `--map-multiplier-no-files VALUE` | Multiplier for map tokens when no files are specified (default: 2) | `AIDER_MAP_MULTIPLIER_NO_FILES` | |

### History Files

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--input-history-file INPUT_HISTORY_FILE` | Specify the chat input history file (default: `.aider.input.history`) | `AIDER_INPUT_HISTORY_FILE` | |
| `--chat-history-file CHAT_HISTORY_FILE` | Specify the chat history file (default: `.aider.chat.history.md`) | `AIDER_CHAT_HISTORY_FILE` | |
| `--restore-chat-history` | Restore the previous chat history messages (default: False) | `AIDER_RESTORE_CHAT_HISTORY` | `--no-restore-chat-history` |
| `--llm-history-file LLM_HISTORY_FILE` | Log the conversation with the LLM to this file (e.g., `.aider.llm.history`) | `AIDER_LLM_HISTORY_FILE` | |

### Output Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--dark-mode` | Use colors suitable for a dark terminal background (default: False) | `AIDER_DARK_MODE` | |
| `--light-mode` | Use colors suitable for a light terminal background (default: False) | `AIDER_LIGHT_MODE` | |
| `--pretty` | Enable/disable pretty, colorized output (default: True) | `AIDER_PRETTY` | `--no-pretty` |
| `--stream` | Enable/disable streaming responses (default: True) | `AIDER_STREAM` | `--no-stream` |
| `--user-input-color VALUE` | Set the color for user input (default: `#00cc00`) | `AIDER_USER_INPUT_COLOR` | |
| `--tool-output-color VALUE` | Set the color for tool output (default: None) | `AIDER_TOOL_OUTPUT_COLOR` | |
| `--tool-error-color VALUE` | Set the color for tool error messages (default: `#FF2222`) | `AIDER_TOOL_ERROR_COLOR` | |
| `--tool-warning-color VALUE` | Set the color for tool warning messages (default: `#FFA500`) | `AIDER_TOOL_WARNING_COLOR` | |
| `--assistant-output-color VALUE` | Set the color for assistant output (default: `#0088ff`) | `AIDER_ASSISTANT_OUTPUT_COLOR` | |
| `--completion-menu-color COLOR` | Set the color for the completion menu (default: terminal’s default text color) | `AIDER_COMPLETION_MENU_COLOR` | |
| `--completion-menu-bg-color COLOR` | Set the background color for the completion menu (default: terminal’s default background color) | `AIDER_COMPLETION_MENU_BG_COLOR` | |
| `--completion-menu-current-color COLOR` | Set the color for the current item in the completion menu (default: terminal’s default background color) | `AIDER_COMPLETION_MENU_CURRENT_COLOR` | |
| `--completion-menu-current-bg-color COLOR` | Set the background color for the current item in the completion menu (default: terminal’s default text color) | `AIDER_COMPLETION_MENU_CURRENT_BG_COLOR` | |
| `--code-theme VALUE` | Set the markdown code theme (default: `default`; other options include `monokai`, `solarized-dark`, `solarized-light`) | `AIDER_CODE_THEME` | |
| `--show-diffs` | Show diffs when committing changes (default: False) | `AIDER_SHOW_DIFFS` | |

### Git Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--git` | Enable/disable looking for a git repo (default: True) | `AIDER_GIT` | `--no-git` |
| `--gitignore` | Enable/disable adding `.aider*` to `.gitignore` (default: True) | `AIDER_GITIGNORE` | `--no-gitignore` |
| `--aiderignore AIDERIGNORE` | Specify the aider ignore file (default: `.aiderignore` in git root) | `AIDER_AIDERIGNORE` | |
| `--subtree-only` | Only consider files in the current subtree of the git repository (default: False) | `AIDER_SUBTREE_ONLY` | |
| `--auto-commits` | Enable/disable auto commit of LLM changes (default: True) | `AIDER_AUTO_COMMITS` | `--no-auto-commits` |
| `--dirty-commits` | Enable/disable commits when repo is found dirty (default: True) | `AIDER_DIRTY_COMMITS` | `--no-dirty-commits` |
| `--attribute-author` | Attribute aider code changes in the git author name (default: True) | `AIDER_ATTRIBUTE_AUTHOR` | `--no-attribute-author` |
| `--attribute-committer` | Attribute aider commits in the git committer name (default: True) | `AIDER_ATTRIBUTE_COMMITTER` | `--no-attribute-committer` |
| `--attribute-commit-message-author` | Prefix commit messages with ‘aider: ‘ if aider authored the changes (default: False) | `AIDER_ATTRIBUTE_COMMIT_MESSAGE_AUTHOR` | `--no-attribute-commit-message-author` |
| `--attribute-commit-message-committer` | Prefix all commit messages with ‘aider: ‘ (default: False) | `AIDER_ATTRIBUTE_COMMIT_MESSAGE_COMMITTER` | `--no-attribute-commit-message-committer` |
| `--commit` | Commit all pending changes with a suitable commit message, then exit (default: False) | `AIDER_COMMIT` | |
| `--commit-prompt PROMPT` | Specify a custom prompt for generating commit messages | `AIDER_COMMIT_PROMPT` | |
| `--dry-run` | Perform a dry run without modifying files (default: False) | `AIDER_DRY_RUN` | `--no-dry-run` |
| `--skip-sanity-check-repo` | Skip the sanity check for the git repository (default: False) | `AIDER_SKIP_SANITY_CHECK_REPO` | |

### Fixing and Committing

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--lint` | Lint and fix provided files, or dirty files if none provided (default: False) | `AIDER_LINT` | |
| `--lint-cmd` | Specify lint commands to run for different languages, e.g., `python: flake8 --select=...` (can be used multiple times) | `AIDER_LINT_CMD` | |
| `--auto-lint` | Enable/disable automatic linting after changes (default: True) | `AIDER_AUTO_LINT` | `--no-auto-lint` |
| `--test-cmd VALUE` | Specify command to run tests | `AIDER_TEST_CMD` | |
| `--auto-test` | Enable/disable automatic testing after changes (default: False) | `AIDER_AUTO_TEST` | `--no-auto-test` |
| `--test` | Run tests and fix problems found (default: False) | `AIDER_TEST` | |

### Analytics

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--analytics` | Enable/disable analytics for one session (default: False) | `AIDER_ANALYTICS` | `--no-analytics` |
| `--analytics-log ANALYTICS_LOG_FILE` | Specify a file to log analytics events | `AIDER_ANALYTICS_LOG` | |
| `--analytics-disable` | Permanently disable analytics (default: False) | `AIDER_ANALYTICS_DISABLE` | |

### Other Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--file FILE` | Specify a file to edit (can be used multiple times) | `AIDER_FILE` | |
| `--read FILE` | Specify a read-only file (can be used multiple times) | `AIDER_READ` | |
| `--vim` | Use VI editing mode in the terminal (default: False) | `AIDER_VIM` | |
| `--chat-language CHAT_LANGUAGE` | Specify the language to use in the chat (default: None, uses system settings) | `AIDER_CHAT_LANGUAGE` | |
| `--version` | Show the version number and exit | | |
| `--just-check-update` | Check for updates and return status in the exit code (default: False) | `AIDER_JUST_CHECK_UPDATE` | |
| `--check-update` | Check for new aider versions on launch (default: True) | `AIDER_CHECK_UPDATE` | `--no-check-update` |
| `--install-main-branch` | Install the latest version from the main branch (default: False) | `AIDER_INSTALL_MAIN_BRANCH` | |
| `--upgrade` | Upgrade aider to the latest version from PyPI (default: False) | `AIDER_UPGRADE` | `--update` |
| `--apply FILE` | Apply the changes from the given file instead of running the chat (debug) | `AIDER_APPLY` | |
| `--apply-clipboard-edits` | Apply clipboard contents as edits using the main model’s editor format (default: False) | `AIDER_APPLY_CLIPBOARD_EDITS` | |
| `--yes-always` | Always say yes to every confirmation | `AIDER_YES_ALWAYS` | |
| `--verbose` | Enable verbose output (default: False) | `AIDER_VERBOSE` | `-v` |
| `--show-repo-map` | Print the repo map and exit (debug) (default: False) | `AIDER_SHOW_REPO_MAP` | |
| `--show-prompts` | Print the system prompts and exit (debug) (default: False) | `AIDER_SHOW_PROMPTS` | |
| `--exit` | Do all startup activities then exit before accepting user input (debug) | `AIDER_EXIT` | |
| `--message COMMAND` | Specify a single message to send the LLM, process reply then exit (disables chat mode) | `AIDER_MESSAGE` | `--msg`, `-m` |
| `--message-file MESSAGE_FILE` | Specify a file containing the message to send the LLM, process reply, then exit (disables chat mode) | `AIDER_MESSAGE_FILE` | `-f` |
| `--load LOAD_FILE` | Load and execute commands from a file on launch | `AIDER_LOAD` | |
| `--encoding VALUE` | Specify the encoding for input and output (default: `utf-8`) | `AIDER_ENCODING` | |
| `--config CONFIG_FILE` | Specify the config file (default: search for `.aider.conf.yml` in git root, cwd, or home directory) | `AIDER_CONFIG_FILE` | `-c` |
| `--gui` | Run aider in your browser (default: False) | `AIDER_GUI` | `--no-gui`, `--browser`, `--no-browser` |
| `--suggest-shell-commands` | Enable/disable suggesting shell commands (default: True) | `AIDER_SUGGEST_SHELL_COMMANDS` | `--no-suggest-shell-commands` |
| `--fancy-input` | Enable/disable fancy input with history and completion (default: True) | `AIDER_FANCY_INPUT` | `--no-fancy-input` |

### Voice Settings

| Option | Description | Environment Variable | Aliases |
|--------|-------------|----------------------|---------|
| `--voice-format VOICE_FORMAT` | Audio format for voice recording (default: `wav`). `webm` and `mp3` require `ffmpeg` | `AIDER_VOICE_FORMAT` | |
| `--voice-language VOICE_LANGUAGE` | Specify the language for voice using ISO 639-1 code (default: `auto`) | `AIDER_VOICE_LANGUAGE` | |

### LLM Keys

Aider has special support for providing OpenAI and Anthropic API keys via command-line switches and YAML config files. All other LLM providers must have their keys and settings specified in environment variables. This can be done in your shell or by using a `.env` file.

## Conclusion

This configuration reference serves as a comprehensive guide to all available options in the `aider` CLI tool. By understanding and utilizing these options, you can customize `aider` to fit your specific development needs and workflows. For a full list of options and more detailed descriptions, you can always use the `aider --help` command.

---

*This document provides a detailed overview of the configuration options available for the `aider` CLI tool. Customize and utilize these options to enhance your development experience.*