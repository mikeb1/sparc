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

The framework uses LiteLLM for advanced AI model integration:

Model Configuration:
- Default model: claude-3-sonnet-20240229
- Model selection via --model flag
- Configurable temperature (default: 0.7)
- Configurable max tokens (default: 4000)
- API key management via environment variables

Progress Tracking:
- Real-time progress bars using tqdm
- Character count reporting for generated files
- Detailed logging of generation steps
- Error handling with specific error messages

Implementation Features:
- Test-Driven Development (TDD) workflow
- Component-by-component implementation
- Automatic test generation and execution
- Real-time progress feedback
- Comprehensive error handling:
  - Model API errors
  - File I/O errors
  - Test failures
  - Timeout handling
  - Process management

Aider Integration:
- AI-powered code generation
- Diff-based code editing
- Auto-confirmation of changes
- Timeout protection (5 minutes per component)
- Detailed logging of changes
