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
The CLI uses advanced AI models to generate comprehensive architecture documentation for any project type:

Project Categories:
- Backend services (REST APIs, GraphQL, etc.)
- Frontend applications (SPA, SSR, etc.)
- Real-time systems (WebSocket, Event-driven)
- Cross-platform applications
- Specialized systems (AI agents, distributed systems)

Generation Process:
1. Analyzes project description
2. Detects technology stack
3. Creates uniquely named output directory (architecture_YYYYMMDD_HHMMSS_project-name)
4. Generates documentation files with progress tracking
5. Reports character count for each generated file

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

## Implementation Features

Code Generation:
- Automatic source code generation
- Test suite generation
- Component separation and organization
- Type definitions and interfaces

Agent System Features:
- Multi-agent management
- Agent delegation
- Monitoring and logging
- State persistence
- Error handling and reporting

Testing Features:
- Automated test generation
- Component-level unit tests
- Service integration tests
- Error scenario coverage

## LiteLLM Integration

Advanced AI Model Integration:

Supported Models:
- Claude 3 Opus (claude-3-opus-20240229)
  - Best for complex architectures
  - Highest reasoning capability
  - Longer context window
- Claude 3 Sonnet (claude-3-sonnet-20240229)
  - Default choice
  - Balanced performance
  - Cost-effective
- GPT-4 (gpt-4)
  - Alternative option
  - Strong reasoning
- GPT-4 Turbo (gpt-4-turbo)
  - Faster processing
  - Recent knowledge

Configuration Options:
- Temperature control (0.0-1.0)
- Max tokens limit
- API key management
- Response streaming
- Custom prompts
