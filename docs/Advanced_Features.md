# Advanced Features

## Custom Guidance Files

Create custom guidance files to control generation:
```toml
[specification]
content = """
Custom project specifications
"""
```

## Architecture Generation
The CLI supports generating architecture for various project types:
- Backend services (FastAPI, Express, etc.)
- Frontend applications (React, Vue, etc.)
- Specialized systems (swarm agents, websockets, etc.)
- Cross-platform applications

Generated files include:
- Specification.md
- Architecture.md
- Pseudocode.md
- Refinement.md
- Completion.md
- guidance.toml

## Git Integration

Advanced Git features:
- Automatic repository initialization
- Commit management
- Dirty state handling

## Testing Integration

Automated testing features:
- Test generation
- Test running
- Coverage tracking

## LiteLLM Integration

Advanced model configuration:
Supported models:
- Claude 3 Opus (claude-3-opus-20240229)
- Claude 3 Sonnet (claude-3-sonnet-20240229)
- GPT-4 (gpt-4)
- GPT-4 Turbo (gpt-4-turbo)
- Temperature control
- Token limits
- API key management
